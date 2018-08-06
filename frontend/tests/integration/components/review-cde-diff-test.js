import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | review cde diff', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    this.set('key', 'test');
    this.set('differences', {
      test: {
        current: 'Current Value',
        original: 'Original Value'
      }
    });

    await render(hbs`{{review-cde-diff key=key differences=differences}}`);
    assert.ok(find('.cde-diff'));
    assert.equal(findAll('.cde-diff .pr-3').length, 2, 'it has a current and original difference');

    this.set('differences', {});
    assert.equal(findAll('.cde-diff .pr-3').length, 0, 'it now has no differences');
  });
});
