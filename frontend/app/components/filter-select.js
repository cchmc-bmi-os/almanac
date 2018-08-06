import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import { A } from '@ember/array';

export default Component.extend({
  // the search-filters service to store the filters
  searchFilters: service('search-filters'),

  // the class names for the root element
  classNames: ['filter', 'form-group'],

  // the variable name of the filter select (should be passed in)
  name: null,

  // the data for the list to display (should be passed in)
  data: A([]),

  // the property of what to display (should be passed in)
  labelPath: null,

  // the location of the selected data (should be passed in)
  value: null,

  // the label of the filter form group (should be passed in)
  label: null,

  // the text to display in the help popover (should be passed in)
  popover: null,

  /**
   * The placeholder computed from the label property
   *
   * @public
   * @return {string}
   */
  placeholder: computed('label', {
    get() {
      return `Select a ${this.get('label')}`;
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
     * in the power-select component
     *
     * @public
     * @param  {object} value
     */
    updateFilter(value) {
      this.get('searchFilters').saveFilter(this.get('name'), value);
      this.set('selected', value);
    }
  }
});
