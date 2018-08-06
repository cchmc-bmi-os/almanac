import Component from '@ember/component';
import { inject as service } from '@ember/service';

export default Component.extend({
  savedCdes: service('saved-cdes'),
  formId: 0,
  sectionId: 0,
  cde: null,
  actions: {
    remove() {
      this.get('savedCdes').removeCde(this.get('formId'), this.get('sectionId'), this.get('cde'));
    }
  }
});
