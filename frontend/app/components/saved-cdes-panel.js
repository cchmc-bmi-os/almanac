import Component from '@ember/component';
import { run } from '@ember/runloop';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Config from 'almanac/config/environment';

export default Component.extend({
  savedCdes: service('saved-cdes'),
  classNames: ['saved-cdes'],
  classNameBindings: ['showSavedCdes'],
  showSavedCdes: false,
  expandAllIcon: computed('savedCdes.expandAllInProgress', {
    get() {
      return this.get('savedCdes.expandAllInProgress') ? 'fa-spinner fa-spin' : 'fa-plus';
    }
  }),
  collapseAllIcon: computed('savedCdes.collapseAllInProgress', {
    get() {
      return this.get('savedCdes.collapseAllInProgress') ? 'fa-spinner fa-spin' : 'fa-minus';
    }
  }),
  exportBase: `${Config.api.host}/${Config.api.namespace}/saved-cdes/`,
  actions: {
    // toggleSavedCdes() {
    //   this.toggleProperty('showSavedCdes');
    // },
    clearSavedCdes() {
      this.get('savedCdes').clearAll();
    },
    expandAllCdes() {
      this.get('savedCdes').expandAll();
    },
    collapseAllCdes() {
      this.get('savedCdes').collapseAll();
    },
    toggleOrdering() {
      this.get('savedCdes').expandForms();
      this.toggleProperty('savedCdes.isOrdering');
    },
    cancelOrdering() {
      this.get('savedCdes').resetOrder();
      this.toggleProperty('savedCdes.isOrdering');
    },
    saveOrdering() {
      this.get('savedCdes').saveOrder();
      run.later(() => {
        this.toggleProperty('savedCdes.isOrdering');
      }, 100);
    },
    updateOrdering(savedCdes) {
      this.get('savedCdes').updateOrder(savedCdes);
    }
  }
});
