import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  // the service to hold the search filters
  searchFilters: service('search-filters'),

  // the default class names for the component
  classNames: ['filter', 'form-group'],

  /**
   * Compute the placeholder text based upon the given label
   * @public
   */
  placeholder: computed('label', {
    get() {
      return `Enter in a ${this.get('label')}`;
    }
  }),

  // /**
  //  * Enable the popover bootstrap element when inserted
  //  * @private
  //  */
  // didInsertElement() {
  //   this._super(...arguments);

  //   this.$('.da-popover').popover({
  //     container: 'body',
  //     trigger: 'focus',
  //     title: this.get('label'),
  //     content: this.get('popover'),
  //     placement: 'bottom'
  //   });
  // },

  // /**
  //  * Clean up the popover when the component is destroyed
  //  * @private
  //  */
  // willDestroyElement() {
  //   this._super(...arguments);

  //   this.$('.da-popover').popover('dispose');
  // },

  actions: {
    /**
     * Updates the filter in the search-filters service and sets the value
     * in the input element
     *
     * @public
     * @param  {object} value
     */
    updateFilters(value, wholeWord) {
      this.set('value', value);
      this.get('searchFilters').saveFilter(this.get('name'), this.get('value'));

      if (typeof (wholeWord) === 'boolean') {
        this.toggleProperty('wholeWord');
      } else if (value === null) {
        this.set('wholeWord', false);
      }

      this.get('searchFilters').saveFilter(`${this.get('name')}WholeWord`, this.get('wholeWord'));
    }
  }
});
