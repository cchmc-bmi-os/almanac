import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import { A } from '@ember/array';

export default Component.extend({
  // the search-filters service
  searchFilters: service('search-filters'),

  // the saved cdes service
  savedCdes: service('saved-cdes'),

  // the default class names for the the component
  classNames: ['results'],

  // the site question data to display (should be passed in)
  siteQuestions: A([]),

  addAllIcon: computed('savedCdes.addAllInProgress', {
    get() {
      return this.get('savedCdes.addAllInProgress') ? 'fa-spinner fa-spin' : 'fa-plus';
    }
  }),

  /**
   * This will return the current page the resuls set is on
   * which is saved in the search filters service
   *
   * @public
   * @return {int}
   */
  page: computed('searchFilters.page', {
    get() {
      return this.get('searchFilters.page');
    }
  }),

  /**
   * This will return the computed number of pages based on the total number
   * of questions and the page_size property in the search filters service.
   * It will take the ceiling of the decimal to get a integer.
   *
   * @public
   * @return {int}
   */
  pages: computed('searchFilters.page_size', 'total', {
    get() {
      return Math.ceil(this.get('total').replace(',', '') / this.get('searchFilters.page_size'));
    }
  }),

  actions: {
    /**
     * This will set the page size in the search filter service as well as set the
     * current page to 1.  It will then refresh the results
     *
     * @public
     * @param {int} size
     */
    setPageSize(size) {
      this.get('searchFilters').saveFilter('page_size', size);
      this.get('searchFilters').saveFilter('page', 1);

      // refresh the results
      this.get('showResults')(true);
    },

    /**
     * This will set the page based on the pagination action that is given.  It
     * will set the property in the search filters service.  It will then refresh
     * the results as well.
     *
     * @public
     */
    setPage(action) {
      switch (action) {
        case 'first':
          this.get('searchFilters').saveFilter('page', 1);
          break;
        case 'previous':
          this.get('searchFilters').saveFilter('page', this.get('page') - 1);
          break;
        case 'next':
          this.get('searchFilters').saveFilter('page', this.get('page') + 1);
          break;
        case 'last':
          this.get('searchFilters').saveFilter('page', this.get('pages'));
          break;
      }

      // refresh the results
      this.get('showResults')(true);
    },

    addAllSavedCdes() {
      if (!this.get('savedCdes.addAllInProgress')) {
        this.get('savedCdes').addAllCdes();
      }
    }
  }
});
