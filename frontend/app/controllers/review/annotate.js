import { alias } from '@ember/object/computed';
import $ from 'jquery';
import Controller from '@ember/controller';
import { computed, get, set } from '@ember/object';
import { isEmpty } from '@ember/utils';
import Config from 'almanac/config/environment';
import { task } from 'ember-concurrency';

export default Controller.extend({
  queryParams: ['page'],
  page: 1,
  pagination: computed({
    get() {
      return {
        perPage: 15
      };
    }
  }),
  filter: null,
  review: alias('model.reviewVersion.review'),
  counts: computed('model.reviewVersion', {
    get() {
      let contents = this.get('model.reviewVersion.contents');

      if (contents) {
        return {
          different: contents.different.length,
          not_found: contents.not_found.length,
          found: contents.found.length
        };
      }

      return {
        different: 0,
        not_found: 0,
        found: 0
      };
    }
  }),

  data: computed('model.{reviewVersion,type}', 'filter', 'page', {
    get() {
      let filter = this.get('filter');
      let cdes = this.get(`model.reviewVersion.contents.${this.get('model.type')}`).filter((item) => {
        if (isEmpty(filter)) {
          return true;
        }

        let re = new RegExp(filter, 'i');
        if (this.get('model.type') === 'different') {
          return re.test(item.uploaded[0]) || re.test(item.uploaded[4]);
        }

        return re.test(item[0]) || re.test(item[4]);
      });

      // calculate the paginated results
      this.set('pagination.start', (this.get('page') - 1) * this.get('pagination.perPage'));
      this.set('pagination.end', this.get('pagination.start') + this.get('pagination.perPage'));
      this.updatePagination();

      return cdes.slice(this.get('pagination.start'), this.get('pagination.end'));
    }
  }),

  updatePagination() {
    // reset buttons
    this.set('pagination.next-btn', false);
    this.set('pagination.prev-btn', false);

    let filter = this.get('filter');
    let cdes = this.get(`model.reviewVersion.contents.${this.get('model.type')}`).filter((item/* , index, enumerable*/) => {
      if (isEmpty(filter)) {
        return true;
      }

      let re = new RegExp(filter, 'i');
      if (this.get('model.type') === 'different') {
        return re.test(item.uploaded[0]) || re.test(item.uploaded[4]);
      }

      return re.test(item[0]) || re.test(item[4]);
    });

    let total = cdes.length;
    this.set('pagination.total', total);
    if (this.get('pagination.start') > total) {
      this.set('pagination.start', total - this.get('pagination.perPage'));
      this.set('pagination.end', total);
      this.set('page', Math.ceil(total / this.get('pagination.perPage')));
    }

    if (this.get('pagination.end') > total) {
      this.set('pagination.end', total);
    }

    if (this.get('page') > 1) {
      this.set('pagination.prev-btn', true);
    }

    if (this.get('pagination.end') < total - 1)  {
      this.set('pagination.next-btn', true);
    }

    this.set('pagination.displayStart', this.get('pagination.start') + 1);
  },

  applyMarkDone: task(function* (state) {
    this.get('flashMessages').clearMessages();

    let version = this.get('model.reviewVersion');
    let newInfo = `${state} Review`;

    if (state === 'finish') {
      newInfo = 'Completed';
    }

    // only lock it if its not finished
    if (state !== 'finish') {
      version.set('is_locked', true);
    }

    // update the defaultConditions from the controller
    let contents = version.get('contents');
    contents.defaultConditions = this.get('defaultConditions');

    let review = yield version.get('review');
    // update the review status
    review.set('status', newInfo);

    if (state !== 'finish') {
      yield review.save();

      // create the next version from the current version
      let nextVersion = this.store.createRecord('review-version', {
        review,
        revision: parseInt(version.get('revision')) + 1,
        contents,
        info: newInfo,
        actions: isEmpty(version.get('actions')) ? null : version.get('actions'),
        summary: isEmpty(version.get('summary')) ? null : version.get('summary'),
        is_locked: false
      });

      // save it and goto the review menu
      yield nextVersion.save().catch(() => {
        this.get('flashMessages').danger('Could not send email');
      });
      this.get('flashMessages').success('Review updated');
      this.transitionToRoute('review');
    } else {
      let _this = this;
      yield $.ajax({
        url: `${Config.api.host}/${Config.api.namespace}/reviews/${review.id}/final`,
        success() {
          _this.get('flashMessages').success('Review finalized');
          review.save();
          version.save();
          _this.transitionToRoute('review');
        },
        error() {
          version.rollbackAttributes();
          review.rollbackAttributes();
          _this.get('flashMessages').danger('There was a problem with finalizing the review');
        }
      });
    }
  }),

  doAddOperation: task(function* (cdes, datas, sums) {
    let operations = this.get('model.reviewVersion.actions') || {};
    let summary = this.get('model.reviewVersion.summary') || {};

    for (let i = 0; i < cdes.length; i++) {
      if (datas[i].operation === 'suggest_replace') {
        let matches = window.location.href.match(/(^https?:\/\/[a-zA-z:0-9]+)\/.*/);
        datas[i].additional = matches[1] + this.get('target').router.generate('cde-view', datas[i].additional);
      }

      let duplicate = false;
      if (operations[cdes[i]]) {
        operations[cdes[i]].forEach((operation) => {
          if (get(operation, 'operation') === get(datas[i], 'operation')) {
            duplicate = true;
          }
        });
      }

      if (!duplicate) {
        if (!summary[cdes[i]]) {
          summary[cdes[i]] = [];
        }

        if (!operations[cdes[i]]) {
          operations[cdes[i]] = [];
        }

        operations[cdes[i]].push(datas[i]);
        summary[cdes[i]].push(sums[i]);
      }
    }

    // filter duplicates
    [operations, summary] = this.filterDuplicates(cdes, operations, summary);

    this.set('model.reviewVersion.actions', operations);
    this.set('model.reviewVersion.summary', summary);
    yield this.get('model.reviewVersion').save();
  }),

  filterDuplicates(cdes, operations, summary) {
    cdes.forEach((cde) => {
      let foundConditions = [];
      operations[cde].forEach((op, opIdx) => {
        if (foundConditions.indexOf(`${get(op, 'operation')}-${get(op, 'additional')}`) === -1) {
          // add to found conditions
          foundConditions.push(`${get(op, 'operation')}-${get(op, 'additional')}`);
        } else {
          // duplicate found, remove it and the summary for it
          operations[cde].splice(opIdx, 1);
          summary[cde].splice(opIdx, 1);
        }
      });
    });

    return [operations, summary];
  },

  actions: {
    addOperation(cdes, datas, sums) {
      this.get('doAddOperation').perform(cdes, datas, sums);
    },
    removeOperation(cde, operation) {
      let version = this.get('model.reviewVersion');
      let operations = version.get('actions');
      let summary = version.get('summary');
      let info = version.get('info');

      // find and remove the element
      let index = operations[cde].indexOf(operation);
      if (index >= 0) {
        if (info === 'Grantee Review') {
          set(operations[cde][index], 'accepted', false);
        } else {
          // remove the element
          operations[cde].splice(index, 1);

          // TODO: Make sure this works
          if (summary[cde][operation.operation]) {
            delete summary[cde][operation.operation];
          }

          // remove the empty property
          if (isEmpty(operations[cde])) {
            delete operations[cde];
          }
        }
      }

      // save the updates
      version.set('actions', operations);
      version.set('summary', summary);
      version.save();
    },
    clearOperations(cde) {
      let version = this.get('model.reviewVersion');
      let operations = version.get('actions');
      let summary = version.get('summary');
      let info = version.get('info');

      if (info === 'Grantee Review') {
        operations[cde].forEach((op) => {
          set(op, 'accepted', false);
        });
      } else {
        // remove the actions for the cde
        delete operations[cde];
        delete summary[cde];
      }

      // save the updates
      version.set('actions', operations);
      version.save();
    },
    clearFilter() {
      this.set('filter', null);
    },
    handlePagination(type) {
      let currentPage = this.get('page');
      if (type === 'next') {
        this.set('page', currentPage + 1);
      } else if (type === 'prev') {
        this.set('page', currentPage - 1);
      }

      // calculate the paginated results
      this.set('pagination.start', (this.get('page') - 1) * this.get('pagination.perPage'));
      this.set('pagination.end', this.get('pagination.start') + this.get('pagination.perPage'));
    },
    showMarkDone() {
      this.set('showDoneConfirmation', true);
    },
    markDone(state) {
      this.get('applyMarkDone').perform(state);
    },
    updateDefaultConditions(value) {
      // update the condtions
      this.set('defaultConditions', value);

      // get the version
      let version = this.get('model.reviewVersion');

      // update the defaultConditions on the version
      let contents = version.get('contents');
      contents.defaultConditions = value;
      version.set('contents', contents);
      version.save();
    }
  }
});
