document.addEventListener('DOMContentLoaded', () => {
    // --- 1. DOM Element References ---
    const addItemBtn = document.getElementById('addItemBtn');
    const accountNameInput = document.getElementById('accountName');
    const goalAmountInput = document.getElementById('goalAmount');
    const priorityInput = document.getElementById('priority'); // Still exists, but largely overridden by drag-and-drop
    const zenWeightInput = document.getElementById('zenWeight');
    const daysRemainingInput = document.getElementById('daysRemaining');
    
    const accountsTableBody = document.getElementById('accountsTableBody');
    
    const amountToDistributeInput = document.getElementById('amountToDistribute');
    const distributionCyclesInput = document.getElementById('distributionCyclesInput'); // For multi-cycle
    const distributeBtn = document.getElementById('distributeBtn');
    const distributionMessage = document.getElementById('distributionMessage');
    
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');
    const csvFileInput = document.getElementById('csvFileInput');
    const importCsvBtn = document.getElementById('importCsvBtn');
    const importMessage = document.getElementById('importMessage');

    // --- 2. Global-like variables ---
    let accounts = JSON.parse(localStorage.getItem('accountsNinjaDB')) || [];
    let draggedItem = null; // For drag-and-drop: the <tr> element
    let draggedItemAccountId = null; // For drag-and-drop: the ID of the account in the dragged <tr>

    // --- 3. Core Data Functions ---
    function saveAccounts() {
        localStorage.setItem('accountsNinjaDB', JSON.stringify(accounts));
    }

    function updatePriorities() {
        // Ensure priorities are sequential (1-based) based on current array order
        accounts.forEach((account, index) => {
            account.priority = index + 1;
        });
    }

    // --- 4. Rendering Function ---
    function renderAccounts() {
        accountsTableBody.innerHTML = ''; // Clear existing rows
        if (accounts.length === 0) {
            const row = accountsTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 8; // Adjusted colspan if needed
            cell.textContent = 'No accounts yet. Add some!';
            cell.style.textAlign = 'center';
            return;
        }

        accounts.forEach((account) => {
            const row = accountsTableBody.insertRow();
            row.dataset.accountId = account.id; // For identifying rows during drag-drop

            // Make row draggable
            row.draggable = true;
            row.addEventListener('dragstart', handleDragStart);
            row.addEventListener('dragover', handleDragOver);
            row.addEventListener('dragleave', handleDragLeave);
            row.addEventListener('drop', handleDrop);
            row.addEventListener('dragend', handleDragEnd);

            row.insertCell().textContent = account.name;
            row.insertCell().textContent = `$${account.goalAmount.toFixed(2)}`;

            const currentAmountCell = row.insertCell();
            const currentAmountInput = document.createElement('input');
            currentAmountInput.type = 'number';
            currentAmountInput.value = account.currentAmount.toFixed(2);
            currentAmountInput.min = 0;
            currentAmountInput.step = "0.01";
            currentAmountInput.addEventListener('change', () => {
                const newValue = parseFloat(currentAmountInput.value);
                if (!isNaN(newValue) && newValue >= 0) {
                    account.currentAmount = newValue;
                    // No need to call updatePriorities here, just save and re-render
                    saveAndRender(); 
                } else {
                    currentAmountInput.value = account.currentAmount.toFixed(2); // revert if invalid
                }
            });
            currentAmountCell.appendChild(currentAmountInput);

            row.insertCell().textContent = `$${Math.max(0, account.goalAmount - account.currentAmount).toFixed(2)}`;
            
            // Display auto-managed priority
            const priorityCellDisplay = row.insertCell();
            priorityCellDisplay.textContent = account.priority;

            const zenCell = row.insertCell();
            const zenValueInput = document.createElement('input');
            zenValueInput.type = 'number';
            zenValueInput.step = '0.1';
            zenValueInput.min = '1';
            zenValueInput.max = '3';
            zenValueInput.value = account.zenWeight;
            zenValueInput.addEventListener('change', () => {
                const newValue = parseFloat(zenValueInput.value);
                if (!isNaN(newValue) && newValue >= 1 && newValue <= 3) {
                    account.zenWeight = newValue;
                    saveAndRender();
                } else {
                    zenValueInput.value = account.zenWeight;
                }
            });
            zenCell.appendChild(zenValueInput);

            const daysCell = row.insertCell();
            const daysValueInput = document.createElement('input');
            daysValueInput.type = 'number';
            daysValueInput.value = account.daysRemaining;
            daysValueInput.min = 0;
            daysValueInput.addEventListener('change', () => {
                const newValue = parseInt(daysValueInput.value);
                if (!isNaN(newValue) && newValue >= 0) {
                    account.daysRemaining = newValue;
                    saveAndRender();
                } else {
                    daysValueInput.value = account.daysRemaining;
                }
            });
            daysCell.appendChild(daysValueInput);

            const actionsCell = row.insertCell();
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete';
            deleteBtn.classList.add('delete-btn');
            deleteBtn.addEventListener('click', () => {
                accounts = accounts.filter(acc => acc.id !== account.id);
                updatePriorities(); // Re-calculate priorities after deletion
                saveAndRender();
            });
            actionsCell.appendChild(deleteBtn);
        });
    }

    // --- 5. Feature Functions ---

    // Add Account
    function addAccount() {
        const name = accountNameInput.value.trim();
        const goalAmount = parseFloat(goalAmountInput.value);
        const zenWeight = parseFloat(zenWeightInput.value);
        const daysRemaining = parseInt(daysRemainingInput.value);

        if (!name || isNaN(goalAmount) || isNaN(zenWeight) || isNaN(daysRemaining)) {
            alert('Please fill in Account Name, Goal Amount, Zen Weight, and Days Remaining with valid values.');
            return;
        }
        if (goalAmount <= 0 || zenWeight < 1 || zenWeight > 3 || daysRemaining < 0) {
            alert('Please enter valid values (Goal > 0, Zen 1-3, Days >= 0).');
            return;
        }

        accounts.push({
            id: Date.now() + Math.random(), // More robust unique ID
            name,
            goalAmount,
            currentAmount: 0,
            priority: 0, // Placeholder, will be set by updatePriorities
            zenWeight,
            daysRemaining
        });
        updatePriorities(); // Update all priorities after adding a new account

        // Clear input fields
        accountNameInput.value = '';
        goalAmountInput.value = '';
        priorityInput.value = ''; // This input field is less relevant now
        zenWeightInput.value = '';
        daysRemainingInput.value = '';

        saveAndRender();
    }

    // Distribute Funds (Latest version with specific summary message)
    function distributeFunds() {
        const amountPerCycle = parseFloat(amountToDistributeInput.value);
        const numCyclesRequested = parseInt(distributionCyclesInput.value) || 1;

        if (isNaN(amountPerCycle) || amountPerCycle <= 0) {
            distributionMessage.textContent = 'Please enter a valid amount per cycle.';
            distributionMessage.style.color = 'red';
            return;
        }
        if (numCyclesRequested < 1) {
            distributionMessage.textContent = 'Distribution cycles must be 1 or more.';
            distributionMessage.style.color = 'red';
            return;
        }

        distributionMessage.textContent = '';
        distributionMessage.style.color = 'black';
        let grandTotalDistributed = 0; 
        let cycleReport = [];
        let actualCyclesProcessed = 0;

        for (let currentCycleNumber = 1; currentCycleNumber <= numCyclesRequested; currentCycleNumber++) {
            actualCyclesProcessed = currentCycleNumber;
            let totalToDistributeThisCycle = amountPerCycle;
            let moneyGivenInThisCycle = 0;
            const maxIterationsPerPass = 10;
            let iterationsThisPass = 0;

            const anyAccountNeedsFunding = accounts.some(acc => acc.currentAmount < acc.goalAmount);
            if (!anyAccountNeedsFunding) {
                cycleReport.push(`Cycle ${currentCycleNumber}: All accounts were already full. No distribution attempted.`);
                if (currentCycleNumber < numCyclesRequested) {
                    cycleReport.push(`--- Stopping further cycles as all accounts are funded. ---`);
                }
                break;
            }

            while (totalToDistributeThisCycle > 0.01 && iterationsThisPass < maxIterationsPerPass) {
                iterationsThisPass++;
                let moneyGivenThisPass = 0;
                let eligibleAccountsInLoop = accounts.filter(acc => acc.currentAmount < acc.goalAmount);
                
                if (eligibleAccountsInLoop.length === 0) {
                    break;
                }

                let totalCalculatedWeight = 0;
                eligibleAccountsInLoop.forEach(acc => {
                    const priorityValue = acc.priority;
                    const zenValue = acc.zenWeight;
                    const urgencyValue = 1 / (acc.daysRemaining + 0.001);
                    acc.calculatedWeight = (zenValue * urgencyValue) / priorityValue;
                    totalCalculatedWeight += acc.calculatedWeight;
                });

                if (totalCalculatedWeight === 0) {
                    break;
                }

                for (const acc of eligibleAccountsInLoop) {
                    const needed = acc.goalAmount - acc.currentAmount;
                    if (needed <= 0) continue;
                    const proportionalShare = (acc.calculatedWeight / totalCalculatedWeight) * totalToDistributeThisCycle;
                    const amountToGive = Math.min(proportionalShare, needed);
                    if (amountToGive > 0.009) {
                        acc.currentAmount += amountToGive;
                        moneyGivenThisPass += amountToGive;
                    }
                }
                
                totalToDistributeThisCycle -= moneyGivenThisPass;
                moneyGivenInThisCycle += moneyGivenThisPass;

                if (moneyGivenThisPass < 0.01 && totalToDistributeThisCycle > 0.01) {
                    break;
                }
                if (moneyGivenThisPass === 0 && totalToDistributeThisCycle > 0.01) {
                    break;
                }
            }

            grandTotalDistributed += moneyGivenInThisCycle;
            let cycleMessage = `Cycle ${actualCyclesProcessed}: Actually distributed $${moneyGivenInThisCycle.toFixed(2)}.`;
            if (totalToDistributeThisCycle > 0.01 && moneyGivenInThisCycle < amountPerCycle) {
                cycleMessage += ` ($${totalToDistributeThisCycle.toFixed(2)} of this cycle's $${amountPerCycle.toFixed(2)} amount remained undistributed).`;
            }
            cycleReport.push(cycleMessage);
            
            if (moneyGivenInThisCycle < 0.01 && currentCycleNumber < numCyclesRequested) {
                const stillNeedsFundingAfterCycle = accounts.some(acc => acc.currentAmount < acc.goalAmount);
                if (stillNeedsFundingAfterCycle) {
                    cycleReport.push(`--- Cycle ${actualCyclesProcessed} distributed very little. Stopping further cycles as limited progress is expected. ---`);
                    break;
                } else if (!stillNeedsFundingAfterCycle) {
                    cycleReport.push(`--- All accounts appear to be full after cycle ${actualCyclesProcessed}. Stopping further cycles. ---`);
                    break;
                }
            }
        }
        
        const totalValueOfAllAccounts = accounts.reduce((sum, acc) => sum + acc.currentAmount, 0);
        const theoreticalTotalAttempted = amountPerCycle * actualCyclesProcessed;

        distributionMessage.innerHTML = 
            `<strong>Targeted Distribution:</strong><br/>` +
            `$${amountPerCycle.toFixed(2)} per cycle was processed for ${actualCyclesProcessed} cycle(s), for a targeted total of $${theoreticalTotalAttempted.toFixed(2)}.<br/>` +
            `---<br/>` +
            `<strong>Actual Outcome of this Operation:</strong><br/>` +
            `Actual New Funds Distributed: $${grandTotalDistributed.toFixed(2)}<br/>` +
            `Total Value in All Accounts Now: $${totalValueOfAllAccounts.toFixed(2)}<br/>` +
            `--- Cycle Details ---<br/>` + 
            cycleReport.join('<br/>');
        
        // amountToDistributeInput.value = '';
        saveAndRender();
    }

    // CSV Download
    function downloadCSV() {
        if (accounts.length === 0) {
            alert('No accounts to download.');
            return;
        }
        const headers = ['Account Name', 'Goal Amount ($)', 'Current Amount ($)', 'Remaining to Goal ($)', 'Priority', 'Zen Weight (1-3)', 'Days Remaining'];
        let csvContent = headers.join(',') + '\n';
        accounts.forEach(account => {
            const remainingAmount = Math.max(0, account.goalAmount - account.currentAmount).toFixed(2);
            const row = [
                escapeCsvValue(account.name),
                escapeCsvValue(account.goalAmount.toFixed(2)),
                escapeCsvValue(account.currentAmount.toFixed(2)),
                escapeCsvValue(remainingAmount),
                escapeCsvValue(account.priority),
                escapeCsvValue(account.zenWeight),
                escapeCsvValue(account.daysRemaining)
            ];
            csvContent += row.join(',') + '\n';
        });
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', 'account_ninja_export.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } else {
            alert('CSV download is not supported by your browser.');
        }
    }

    // CSV Import
    function handleImportCSV() {
        const file = csvFileInput.files[0];
        if (!file) {
            importMessage.textContent = 'Please select a CSV file to import.';
            importMessage.style.color = 'red';
            return;
        }
        importMessage.textContent = 'Processing...';
        importMessage.style.color = 'black';

        const reader = new FileReader();
        reader.onload = function(event) {
            const csvData = event.target.result;
            const newAccounts = [];
            let errors = [];
            let importedCount = 0;
            const lines = csvData.split(/\r\n|\n/);
            const startIndex = lines[0].toLowerCase().includes('account name') ? 1 : 0; // Basic header detection

            for (let i = startIndex; i < lines.length; i++) {
                const line = lines[i].trim();
                if (!line) continue;
                const values = parseCsvRowRobust(line);

                // Expected relevant columns: Name, Goal, Current, Zen, Days
                // Assuming fixed order for simplicity, ignoring extra columns
                if (values.length < 5) { 
                    errors.push(`Row ${i + 1}: Not enough columns (found ${values.length}, expected at least 5: Name, Goal, Current, Zen, Days).`);
                    continue;
                }
                
                try {
                    // Mapping based on a common export order: Name, Goal, Current, (skip remaining), (skip priority), Zen, Days
                    // For import, let's be more direct: Name, Goal, Current, Zen, Days
                    const name = values[0];
                    const goalAmount = parseFloat(values[1]);
                    const currentAmount = parseFloat(values[2]);
                    // CSV might have 7 columns from export: Name, Goal, Current, Remaining, Priority, Zen, Days
                    // If so, Zen is values[5], Days is values[6]
                    // If user provides simpler: Name, Goal, Current, Zen, Days, then Zen=values[3], Days=values[4]
                    let zenWeight, daysRemaining;
                    if (values.length >= 7) { // Assuming full export format
                        zenWeight = parseFloat(values[5]);
                        daysRemaining = parseInt(values[6]);
                    } else if (values.length >= 5) { // Assuming Name, Goal, Current, Zen, Days
                         zenWeight = parseFloat(values[3]);
                         daysRemaining = parseInt(values[4]);
                    } else {
                        throw new Error("Not enough columns for Zen and Days.");
                    }


                    if (!name) throw new Error("Account name is missing.");
                    if (isNaN(goalAmount) || goalAmount <= 0) throw new Error("Invalid Goal Amount.");
                    if (isNaN(currentAmount) || currentAmount < 0) throw new Error("Invalid Current Amount.");
                    if (isNaN(zenWeight) || zenWeight < 1 || zenWeight > 3) throw new Error("Invalid Zen Weight (must be 1-3).");
                    if (isNaN(daysRemaining) || daysRemaining < 0) throw new Error("Invalid Days Remaining.");
                    
                    newAccounts.push({
                        id: Date.now() + i + Math.random(),
                        name: name,
                        goalAmount: goalAmount,
                        currentAmount: currentAmount,
                        priority: 0, 
                        zenWeight: zenWeight,
                        daysRemaining: daysRemaining
                    });
                    importedCount++;
                } catch (e) {
                    errors.push(`Row ${i + 1} ("${values[0] || 'Unknown Name'}"): ${e.message}`);
                }
            }

            if (newAccounts.length > 0) {
                accounts = newAccounts;
                updatePriorities();
                saveAndRender();
                importMessage.textContent = `Successfully imported ${importedCount} accounts. Existing accounts overwritten.`;
                importMessage.style.color = 'green';
            } else if (errors.length === 0 && importedCount === 0) {
                importMessage.textContent = 'No valid accounts found in the CSV to import.';
                importMessage.style.color = 'orange';
            }

            if (errors.length > 0) {
                const existingMsg = importMessage.textContent.startsWith('Successfully') ? importMessage.textContent + '<br/>' : '';
                importMessage.innerHTML = `${existingMsg}<strong>Import Errors:</strong><br/>${errors.slice(0,5).join('<br/>')}`;
                if (errors.length > 5) importMessage.innerHTML += `<br/>And ${errors.length - 5} more errors...`;
                importMessage.style.color = newAccounts.length > 0 ? 'orange' : 'red';
                console.error("CSV Import Errors:", errors);
            }
            csvFileInput.value = '';
        };
        reader.onerror = function() {
            importMessage.textContent = 'Failed to read the file.';
            importMessage.style.color = 'red';
            csvFileInput.value = '';
        };
        reader.readAsText(file);
    }

    // Drag and Drop Handlers
    function handleDragStart(e) {
        draggedItem = e.target; // The <tr> element
        draggedItemAccountId = draggedItem.dataset.accountId;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedItemAccountId); // Necessary for Firefox
        setTimeout(() => {
            if (draggedItem) draggedItem.classList.add('dragging');
        }, 0);
    }

    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        const targetRow = e.target.closest('tr');
        if (targetRow && targetRow !== draggedItem && targetRow.dataset.accountId) {
            document.querySelectorAll('#accountsTableBody tr.drag-over').forEach(row => row.classList.remove('drag-over'));
            targetRow.classList.add('drag-over');
        }
    }

    function handleDragLeave(e) {
        const targetRow = e.target.closest('tr');
        if (targetRow) {
            targetRow.classList.remove('drag-over');
        }
    }

    function handleDrop(e) {
        e.preventDefault();
        const targetRow = e.target.closest('tr');
        document.querySelectorAll('#accountsTableBody tr.drag-over').forEach(row => row.classList.remove('drag-over'));

        if (!targetRow || !draggedItem || targetRow === draggedItem || !draggedItemAccountId) {
            if (draggedItem) draggedItem.classList.remove('dragging'); // Clean up if invalid drop
            draggedItem = null;
            draggedItemAccountId = null;
            return;
        }

        const targetAccountId = targetRow.dataset.accountId;
        const draggedAccountIndex = accounts.findIndex(acc => String(acc.id) === String(draggedItemAccountId));
        
        if (draggedAccountIndex === -1) {
            console.error("Could not find dragged item in accounts array.");
            if (draggedItem) draggedItem.classList.remove('dragging');
            draggedItem = null;
            draggedItemAccountId = null;
            return;
        }
        
        const [draggedAccountObject] = accounts.splice(draggedAccountIndex, 1);
        
        // Find new target index after splice
        let targetAccountIndex = accounts.findIndex(acc => String(acc.id) === String(targetAccountId));

        if (targetAccountIndex === -1) { // Should not happen if targetRow is valid
             accounts.push(draggedAccountObject); // Failsafe: add to end
        } else {
            const rect = targetRow.getBoundingClientRect();
            const midpoint = rect.top + rect.height / 2;
            if (e.clientY >= midpoint) { // Dropped on the lower half of the target row, insert after
                accounts.splice(targetAccountIndex + 1, 0, draggedAccountObject);
            } else { // Dropped on the upper half, insert before
                accounts.splice(targetAccountIndex, 0, draggedAccountObject);
            }
        }
        
        updatePriorities();
        saveAndRender();
        // Drag end will clean up draggedItem visuals
    }

    function handleDragEnd(e) {
        if (draggedItem) {
            draggedItem.classList.remove('dragging');
        }
        document.querySelectorAll('#accountsTableBody tr.drag-over').forEach(row => row.classList.remove('drag-over'));
        draggedItem = null;
        draggedItemAccountId = null;
    }

    // --- 6. Helper Functions ---
    function escapeCsvValue(value) {
        if (value == null) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
    }

    function parseCsvRowRobust(rowStr) {
        const result = [];
        let currentField = '';
        let inQuotes = false;
        for (let i = 0; i < rowStr.length; i++) {
            const char = rowStr[i];
            if (char === '"') {
                if (inQuotes && i + 1 < rowStr.length && rowStr[i + 1] === '"') {
                    currentField += '"';
                    i++;
                } else {
                    inQuotes = !inQuotes;
                }
            } else if (char === ',' && !inQuotes) {
                result.push(currentField.trim());
                currentField = '';
            } else {
                currentField += char;
            }
        }
        result.push(currentField.trim());
        return result;
    }

    // --- 7. Utility Function ---
    function saveAndRender() {
        saveAccounts();
        renderAccounts();
    }

    // --- 8. Main Event Listeners ---
    addItemBtn.addEventListener('click', addAccount);
    distributeBtn.addEventListener('click', distributeFunds);
    downloadCsvBtn.addEventListener('click', downloadCSV);
    importCsvBtn.addEventListener('click', handleImportCSV);

    // --- 9. Initial Setup ---
    updatePriorities(); // Ensure priorities are set correctly on initial load or data refresh
    renderAccounts(); // Initial render of the accounts table
});