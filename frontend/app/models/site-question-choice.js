import DS from 'ember-data';

const { attr, belongsTo } = DS;

export default DS.Model.extend({
  ordering: attr('number'),

  site_question: belongsTo('site-question', { async: true }),
  choice: belongsTo('choice', { async: true })
});
