import { computed } from '@ember/object';
import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  name: attr('string'),
  section: attr('string'),

  fullForm: computed('name', 'section', {
    get() {
      let section = this.get('section');
      if (section === null) {
        section = 'None';
      }

      return `${this.get('name')} > ${section}`;
    }
  })
});
