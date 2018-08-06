import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | saved cdes panel', function(hooks) {
  setupRenderingTest(hooks);

  /*

  <div id="ember236" class="saved-cdes ember-view"><div class="tab" data-ember-action="" data-ember-action-237="237">
    <p><span class="count badge badge-primary"><i class="fa fa-spinner fa-pulse"></i></span></p>
    CDE's
  </div>
  <div class="card">
    <div class="card-header">
      <div class="action">
        <button class="btn btn-success" data-ember-action="" data-ember-action-245="245">Clear</button>
      </div>
      Saved CDE's
    </div>
    <hr>
    <p class="text-center card-content">You have no saved CDE's</p>
  </div></div>

  */

  test('it renders', async function(assert) {
    await render(hbs`{{saved-cdes-panel}}`);

    assert.ok(find('.saved-cdes'));
    assert.ok(find('.saved-cdes .tab'));
    assert.ok(find('.saved-cdes .tab .count'));
    assert.ok(find('.saved-cdes .card'));
    assert.equal(find('.saved-cdes .card .card-header').textContent.trim(), 'Clear\n    \n    Saved CDE\'s');
  });
});
