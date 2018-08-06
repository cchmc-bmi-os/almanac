import DS from 'ember-data';

const { attr } = DS;

export default DS.Model.extend({
  name: attr('string'),
  text: attr('string'),
  branching_logic: attr('string'),
  branching_questions: attr('json'),
  choices: attr('json'),
  codes: attr('json'),
  definition: attr('json'),
  all_definitions: attr('json'),
  form: attr('string'),
  section: attr('string'),
  max_val: attr('string'),
  min_val: attr('string'),
  question: attr('string'),
  site: attr('string'),
  tags: attr('json'),
  type: attr('string'),
  unknown_val: attr('string'),
  code_type: attr('string'),
  question_codes: attr('json')
});
