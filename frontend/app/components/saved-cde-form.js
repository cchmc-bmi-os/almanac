import Component from '@ember/component';
import { isEmpty } from '@ember/utils';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  savedCdes: service('saved-cdes'),
  formId: 0,
  form: null,
  expanded: computed('form.expanded', {
    get() {
      return this.get('form.expanded');
    }
  }),
  expandIcon: computed('form.expanded', {
    get() {
      return this.get('form.expanded') ? 'fa-caret-down' : 'fa-caret-right';
    }
  }),
  noSectionCdes: computed('form', {
    get() {
      let sections = this.get('form.sections');

      if (isEmpty(sections[0].name)) {
        return sections[0].cdes;
      }

      return [];
    }
  }),
  noSection: computed('form', {
    get() {
      let sections = this.get('form.sections');

      if (isEmpty(sections[0].name)) {
        return sections[0];
      }

      return null;
    }
  }),
  actions: {
    // toggleExpand() {
    //   this.toggleProperty('expanded');
    //   this.set('form.expanded', this.get('expanded'));
    // },
    remove() {
      this.get('savedCdes').removeForm(this.get('formId'));
    },
    updateOrdering(sections) {
      let noSection = this.get('noSection');

      // add in the no section cdes if there are any
      if (noSection) {
        sections.unshift(noSection);
      }

      this.get('savedCdes').updateSectionOrder(this.get('formId'), sections);
    }
  }
});
