import $ from 'jquery';
import Controller from '@ember/controller';
import { isEmpty } from '@ember/utils';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Config from 'almanac/config/environment';
import { task } from 'ember-concurrency';
import moment from 'moment';

export default Controller.extend({
  session: service(),
  reviewName: null,
  formValid: computed('reviewName', {
    get() {
      return !isEmpty(this.get('reviewName'));
    }
  }),
  initializeReview: task(function* (data) {
    let review = yield this.get('store').createRecord('review', {
      user: data.user,
      name: data.name,
      location: data.location,
      status: 'Calculating Diff',
      started_at: moment()
    });
    yield review.save();

    this.set('review', review);

    // create first version
    let version = yield this.get('store').createRecord('review-version', {
      review,
      revision: 1,
      contents: data.data,
      info: 'Uploaded DD',
      is_locked: false
    });
    yield version.save();
    this.calculateDiff(review.id);
    this.get('flashMessages').success('Review submitted');
    return this.transitionToRoute('review.index');
  }),
  calculateDiff(review) {
    let _this = this;

    return $.ajax({
      url: `${Config.api.host}/${Config.api.namespace}/reviews/${review}/diff`,
      type: 'get',
      dataType: 'json',
      error() {
        _this.get('flashMessages').danger('Could not calculate difference');
      }
    });
  },
  actions: {
    submitReview(data) {
      this.get('initializeReview').perform(data);
    }
  }
});
