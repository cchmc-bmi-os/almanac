import Component from '@ember/component';

export default Component.extend({
  classNames: ['review-list', 'row', 'justify-content-md-center'],
  showReviewConfirm: false,
  currentReview: null,
  actions: {
    showRemovalRequest(review) {
      this.set('currentReview', review);
      this.set('showRemovalConfirm', true);
    },

    requestRemoval() {
      this.get('requestRemoval')(this.get('currentReview'));
      this.send('closeConfirm');
    },

    removeReview(review) {
      this.set('currentReview', review);
      this.set('showReviewConfirm', true);
    },

    closeConfirm() {
      this.set('currentReview', null);
      this.set('showReviewConfirm', false);
      this.set('showRemovalConfirm', false);
    },

    deleteReview() {
      this.get('remove')(this.get('currentReview'));
      this.send('closeConfirm');
    },

    refresh(review) {
      this.get('refresh')(review);
    }
  }
});
