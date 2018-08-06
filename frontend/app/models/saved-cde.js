import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  questions: attr('json'),
  sort: attr('boolean')
});
