import React from 'react';

interface ContactModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ContactModal: React.FC<ContactModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
    >
      <div
        className="bg-transparent p-0 relative max-w-xs w-full shadow-none border-none"
        onClick={e => e.stopPropagation()}        
      >
        <button
          className="absolute top-1 right-1 text-gray-400 hover:text-black text-2xl"
          onClick={onClose}
          aria-label="关闭"
        >
          ×
        </button>
        <h2 className="text-xl font-bold mb-4 text-center"></h2>
        <div className="flex flex-col items-center">
          <img
            src="/icons/qrcode.png"
            alt="二维码"
            className="w-32 h-32 mb-4  rounded"
          />
          <p className="text-gray-700 text-center"></p>
          <p className="text-gray-700 text-center"></p>
        </div>
      </div>
    </div>
  );
};

export default ContactModal;