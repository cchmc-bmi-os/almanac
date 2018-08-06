import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  revision: attr('number'),
  contents: attr('json'),
  summary: attr('json'),
  actions: attr('json'),
  info: attr('string'),
  is_locked: attr('boolean'),

  review: belongsTo('review', { async: true })
});
