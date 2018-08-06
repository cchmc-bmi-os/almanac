import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  // the saved cdes service
  savedCdes: service('saved-cdes'),

  // store the showing of the detail flag @type {boolean}
  showDetail: false,

  // the font awesome icon to display @type {string}
  toggleIcon: computed('showDetail', {
    get() {
      return this.get('showDetail') ? 'caret-down' : 'caret-right';
    }
  }),

  // checks to see if name is in the allCdes property
  existsInSavedCdes: computed('savedCdes.allCdes', {
    get() {
      return this.get('savedCdes.allCdes').indexOf(this.get('siteQuestion.name')) !== -1;
    }
  }),

  actions: {
    addSavedCde() {
      this.get('savedCdes').addCde(this.get('siteQuestion'));
    }
  }
});
