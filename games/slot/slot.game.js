(() => {
  const SLOT = (window.SLOT = window.SLOT || {});

  SLOT.game = {
    applySpin(keys) {
      if (SLOT.ui && typeof SLOT.ui.applyKeys === "function") {
        SLOT.ui.applyKeys(keys);
      }
    }
  };
})();
