import Component from '@ember/component';
import { get, computed } from '@ember/object';
import { isEmpty } from '@ember/utils';
import { htmlSafe } from '@ember/string';

export default Component.extend({
  classNames: ['cde-diff'],
  key: null,

  diff: computed('differences', 'key', {
    get() {
      let key = this.get('key');
      let differences = this.get('differences');

      // console.log('key', key);
      // console.log('differences', differences);

      return differences ? get(differences, key) : null;
    }
  }),
  cdeValue: computed('key', {
    get() {
      const key = this.get('key');
      const value = this.get(`cde.${key}`);

      if (isEmpty(value)) {
        return htmlSafe('<span class="text-muted">None</span>');
      }

      return value;
    }
  })
});
