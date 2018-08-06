import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | review cde item', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    this.set('data', {"uploaded":["u_study_id","Demographics","","text","NBSTRN ID","Autopopulated?","How will this be generated on the MSSM instance?","","","","","","","","","","",""],"database":{"name":"u_study_id","form":"Intake Demographics","section":null,"type":"text","text":"NBSTRN ID","choices":"","note":null,"calculation":null,"min_val":null,"max_val":null,"identifier":"False","branching_logic":null,"required":"False","align":null,"ordering":1,"matrix_name":null,"matrix_ranking":null},"differences":["5"],"possible":[{"id":2987,"name":"u_study_id","text":"NBSTRN ID","site":"IBEMC","similarity":0},{"id":8585,"name":"u_study_id__d","text":"NBSTRN ID","site":"LSD","similarity":3},{"id":8549,"name":"u_study_id__ph","text":"NBSTRN ID","site":"Public Health","similarity":4},{"id":8548,"name":"u_study_id__ph","text":"NBSTRN ID","site":"Public Health","similarity":4},{"id":8389,"name":"nbstrn_id","text":"NBSTRN ID","site":"NBSTRN Core","similarity":5}]});
    this.set('type', 'different');
    this.set('version', '1');

    await render(hbs`{{review-cde-item data=data type=type version=version}}`);
    assert.ok(find('.data-element .card'));
    assert.equal(find('.data-element .card h3.text-primary').textContent.trim(), 'NBSTRN ID', 'it has the correct text');
  });
});
