import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  name: attr('string'),
  description: attr('string'),
  base_url: attr('string'),
  note: attr('string'),

  source: belongsTo('source', { async: true })
});
