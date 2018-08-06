import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  definition: attr('string'),
  note: attr('string'),
  source: belongsTo('source', { async: true })
});
