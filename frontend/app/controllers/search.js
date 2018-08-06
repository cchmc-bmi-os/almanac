import Controller from '@ember/controller';
import $ from 'jquery';
import { inject as service } from '@ember/service';
import { run } from '@ember/runloop';
import Config from 'almanac/config/environment';
import { numberFormat } from 'almanac/helpers/number-format';
import { isEmpty } from '@ember/utils';
import { computed } from '@ember/object';
import { task, timeout } from 'ember-concurrency';


export default Controller.extend({
  // the service to hold the search filters
  searchFilters: service('search-filters'),

  calculateCdeCount: task(function* () {
    this.set('showResults', false);

    yield timeout(250);

    const resp = yield $.get({
      url: `${Config.api.host}/${Config.api.namespace}/questions/count`,
      // contentType: 'application/json',
      data: this.get('searchFilters').requestFilters(),
      dataType: 'json',
    });

    return numberFormat([resp.count]);
  }).restartable(),

  makeCountRequest() {
    // update sections based on form
    if (isEmpty(this.get('searchFilters.form.name'))) {
      // filter for all sections
      this.set('sections', this.get('model.forms').filter((form) => {
        return !isEmpty(form.get('section'));
      }));
    } else {
      // filter for all sections and the form name that is specified
      this.set('sections', this.get('model.forms').filter((form) => {
        return !isEmpty(form.get('section')) && form.get('name') === this.get('searchFilters.form.name');
      }));
    }

    // update the conditions based on the condition category selected
    if (isEmpty(this.get('searchFilters.conditionCategory.name'))) {
      // filter for all conditions
      this.set('conditions', this.store.findAll('condition'));
    } else {
      // filter for all conditions and limit by the condition category selected
      this.set('conditions', this.store.query('condition', { category: this.get('searchFilters.conditionCategory.name') }));
    }
  },

  /**
   * This is the observer to watch the filters for any changes.  When changed it
   * will call the function to update the question counts.
   *
   * @private
   * @return {int}
   */
  cdeCount: computed('searchFilters.{form,section,conditionCategory,condition,keyword,keywordWholeWord,site}', {
    get() {
      return this.get('calculateCdeCount').perform();
    }
  }),

  actions: {
    /**
     * This will show the results element in the DOM and reset the siteQuestions
     * property with the newest questions that are pulled from the api.
     *
     * @public
     */
    showResults(doNotReset = false) {
      if (doNotReset === false) {
        // reset the page to 1
        this.get('searchFilters').saveFilter('page', 1);
      }

      if (this.get('cdeCount.value') < 1) {
        return;
      }

      this.set('showResults', true);
      this.set('siteQuestions', null);

      run.later(() => {
        window.scrollTo(0, document.getElementsByClassName('filters')[0].offsetHeight + 50);
      }, 50);

      this.store.query('site-question', this.get('searchFilters').requestFilters()).then((siteQuestions) => {
        this.set('siteQuestions', siteQuestions);
      });
    },
    /**
     * This will clear all of the filters by calling the clearAllFilters from the
     * search-filters service
     *
     * @public
     */
    clearAllFilters() {
      this.get('searchFilters').clearAllFilters();
      this.set('showResults', false);
      this.notifyPropertyChange('cdeCount');

      window.scrollTo(0, 0);
    }
  }
});
