import { Factory, faker } from 'ember-cli-mirage';

export default Factory.extend({
  align: null,
  branching_logic: faker.lorem.sentence,
  calculation: null,
  matrix_name: null,
  max_val: faker.random.number,
  min_val: faker.random.number,
  name: faker.company.companyName,
  note: null,
  ordering: faker.random.number,
  text: faker.company.catchPhrase,
  type: faker.random.arrayElement(['radio', 'text', 'multiple', 'date']),
  unknown_val: null,
  definition() {
    return {
      version: faker.random.number(),
      source_address: faker.internet.url(),
      definition: faker.company.catchPhrase(),
      source_name: faker.company.bs(),
      source_number: faker.random.number(),
      note: faker.company.companySuffix()
    };
  }
});
