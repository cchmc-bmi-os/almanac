import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  savedCdes: service('saved-cdes'),
  formId: 0,
  sectionId: 0,
  section: null,
  expanded: computed('section.expanded', {
    get() {
      return this.get('section.expanded');
    }
  }),
  expandIcon: computed('section.expanded', {
    get() {
      return this.get('section.expanded') ? 'fa-caret-down' : 'fa-caret-right';
    }
  }),
  sectionIsNotNone: computed('section', {
    get() {
      return this.get('section').name !== 'none';
    }
  }),
  actions: {
    remove() {
      this.get('savedCdes').removeSection(this.get('formId'), this.get('sectionId'));
    }
  }
});
