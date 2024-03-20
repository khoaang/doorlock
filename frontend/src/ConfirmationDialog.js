// ConfirmationDialog.js
import React from 'react';
import Modal from 'react-modal';

Modal.setAppElement('#root'); // This binds your modal to your app root (you might need to adjust the selector depending on your setup)

function ConfirmationDialog({ isOpen, onRequestClose, onConfirm, message }) {
  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      contentLabel="Confirmation"
      className="modal-content"
      overlayClassName="modal-overlay"
    >
      <h2>Confirmation</h2>
      <p>{message}</p>
      <button onClick={onConfirm}>Yes</button>
      <button onClick={onRequestClose}>No</button>
    </Modal>
  );
}

export default ConfirmationDialog;
