/* global Office */

Office.onReady(() => {
  console.log("Commands loaded");
});

function analyzeContract(event) {
  // TODO: Implement command
  console.log("Analyze contract command triggered");
  event.completed();
}

// Register functions
Office.actions.associate("analyzeContract", analyzeContract);