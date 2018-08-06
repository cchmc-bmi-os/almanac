import { underscore } from '@ember/string';
import DS from 'ember-data';

/**
 * This just ensures that the properties are snake_case
 *
 * @public
 */
export default DS.JSONAPISerializer.extend({
  keyForAttribute(attr) {
    return underscore(attr);
  },

  keyForRelationship(rawKey) {
    return underscore(rawKey);
  }
});
