import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  name: attr('string'),
  label: attr('string'),
  ordering: attr('number'),

  category: belongsTo('condition-category', { async: true })
});
