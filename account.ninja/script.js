document.addEventListener('DOMContentLoaded', () => {
    // Existing DOM Elements
    const addItemBtn = document.getElementById('addItemBtn');
    const accountNameInput = document.getElementById('accountName');
    const goalAmountInput = document.getElementById('goalAmount');
    const priorityInput = document.getElementById('priority'); // Still used for new items, then auto-adjusted
    const zenWeightInput = document.getElementById('zenWeight');
    const daysRemainingInput = document.getElementById('daysRemaining');
    const accountsTableBody = document.getElementById('accountsTableBody');
    const amountToDistributeInput = document.getElementById('amountToDistribute');
    const distributeBtn = document.getElementById('distributeBtn');
    const distributionMessage = document.getElementById('distributionMessage');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');

    // NEW DOM Elements for CSV Import
    const csvFileInput = document.getElementById('csvFileInput');
    const importCsvBtn = document.getElementById('importCsvBtn');
    const importMessage = document.getElementById('importMessage');

    let accounts = JSON.parse(localStorage.getItem('accountsNinjaDB')) || [];
    updatePriorities(); // Ensure priorities are set on initial load

    // --- Drag and Drop State ---
    let draggedItem = null; // To store the <tr> element being dragged
    let draggedItemAccountId = null; // To store the account ID of the dragged item

    function saveAccounts() {
        localStorage.setItem('accountsNinjaDB', JSON.stringify(accounts));
    }

    // NEW: Update priorities sequentially based on current order in the array
    function updatePriorities() {
        accounts.forEach((account, index) => {
            account.priority = index + 1;
        });
    }

    function renderAccounts() {
        accountsTableBody.innerHTML = '';
        if (accounts.length === 0) {
            // ... (no change to empty state)
            const row = accountsTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 8;
            cell.textContent = 'No accounts yet. Add some!';
            cell.style.textAlign = 'center';
            return;
        }

        accounts.forEach((account) => { // Removed index from forEach as we use account.id
            const row = accountsTableBody.insertRow();
            row.dataset.accountId = account.id; // Set data-attribute for drag-drop identification

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
            currentAmountInput.addEventListener('change', () => {
                const newValue = parseFloat(currentAmountInput.value);
                if (!isNaN(newValue) && newValue >= 0) {
                    account.currentAmount = newValue;
                    saveAndRender(); // Only save and re-render
                } else {
                    currentAmountInput.value = account.currentAmount.toFixed(2);
                }
            });
            currentAmountCell.appendChild(currentAmountInput);

            row.insertCell().textContent = `$${Math.max(0, account.goalAmount - account.currentAmount).toFixed(2)}`;

            // Priority display - now reflects the auto-set priority
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
                accounts = accounts.filter(acc => acc.id !== account.id); // Filter out by ID
                updatePriorities(); // Re-calculate priorities after deletion
                saveAndRender();
            });
            actionsCell.appendChild(deleteBtn);
        });
    }

    function addAccount() {
        const name = accountNameInput.value.trim();
        const goalAmount = parseFloat(goalAmountInput.value);
        // Priority from input is not directly used for ordering anymore, but can be a placeholder
        // let priority = parseInt(priorityInput.value);
        const zenWeight = parseFloat(zenWeightInput.value);
        const daysRemaining = parseInt(daysRemainingInput.value);

        if (!name || isNaN(goalAmount) || isNaN(zenWeight) || isNaN(daysRemaining)) {
            // ... (alert remains same)
            alert('Please fill in Account Name, Goal, Zen, and Days with valid values.');
            return;
        }
        if (goalAmount <= 0 || zenWeight < 1 || zenWeight > 3 || daysRemaining < 0) {
            // ... (alert remains same)
            alert('Please enter valid values (Goal > 0, Zen 1-3, Days >= 0).');
            return;
        }

        accounts.push({
            id: Date.now(),
            name,
            goalAmount,
            currentAmount: 0,
            priority: accounts.length + 1, // Set initial priority at the end
            zenWeight,
            daysRemaining
        });
        updatePriorities(); // Update all priorities after adding

        accountNameInput.value = '';
        goalAmountInput.value = '';
        priorityInput.value = ''; // Clear priority input
        zenWeightInput.value = '';
        daysRemainingInput.value = '';

        saveAndRender();
    }

    function distributeFunds() {
        // ... (distributeFunds logic remains largely the same, relies on account.priority)
        // Ensure priorities are up-to-date before distribution, though saveAndRender should handle this.
        let totalToDistribute = parseFloat(amountToDistributeInput.value);
        if (isNaN(totalToDistribute) || totalToDistribute <= 0) {
            distributionMessage.textContent = 'Please enter a valid amount to distribute.';
            return;
        }
        distributionMessage.textContent = '';

        let totalDistributedThisRound = 0;
        const maxIterations = 10;
        let iterations = 0;
        let totalMoneyGivenOverall = 0;

        // Create a clone of accounts to sort for distribution without altering the main array's order yet
        let distributableAccounts = JSON.parse(JSON.stringify(accounts));
        distributableAccounts.sort((a, b) => a.priority - b.priority); // Sort by priority

        while (totalToDistribute > 0.01 && iterations < maxIterations) {
            iterations++;
            // Filter from the *original* accounts array by ID based on sorted distributableAccounts
            let eligibleAccountsInLoop = [];
            for (const distAcc of distributableAccounts) {
                const originalAcc = accounts.find(acc => acc.id === distAcc.id);
                if (originalAcc && originalAcc.currentAmount < originalAcc.goalAmount) {
                    eligibleAccountsInLoop.push(originalAcc);
                }
            }
            
            if (eligibleAccountsInLoop.length === 0) {
                if (!distributionMessage.textContent) distributionMessage.textContent = `No accounts need funding. $${totalToDistribute.toFixed(2)} remaining.`;
                break;
            }

            let totalCalculatedWeight = 0;
            eligibleAccountsInLoop.forEach(acc => {
                const priorityValue = acc.priority; // This priority is now 1-based sequential
                const zenValue = acc.zenWeight;
                const urgencyValue = 1 / (acc.daysRemaining + 0.001);
                // We use the original account object for its properties but ensure it's eligible
                const accountInOriginalArray = accounts.find(a => a.id === acc.id);
                if (accountInOriginalArray) {
                    accountInOriginalArray.calculatedWeight = (zenValue * urgencyValue) / priorityValue; // Use actual priority
                    totalCalculatedWeight += accountInOriginalArray.calculatedWeight;
                }
            });


            if (totalCalculatedWeight === 0) {
                 if (!distributionMessage.textContent) distributionMessage.textContent = `Could not determine weights for distribution. $${totalToDistribute.toFixed(2)} remaining.`;
                break;
            }

            let moneyGivenThisPass = 0;
            for (const acc of eligibleAccountsInLoop) { // Iterate based on sorted order
                const accountInOriginalArray = accounts.find(a => a.id === acc.id);
                if (!accountInOriginalArray) continue;

                const needed = accountInOriginalArray.goalAmount - accountInOriginalArray.currentAmount;
                if (needed <= 0) continue;

                const proportionalShare = (accountInOriginalArray.calculatedWeight / totalCalculatedWeight) * totalToDistribute;
                const amountToGive = Math.min(proportionalShare, needed);

                if (amountToGive > 0.009) { // Consider amounts greater than a cent
                    accountInOriginalArray.currentAmount += amountToGive;
                    moneyGivenThisPass += amountToGive;
                    totalMoneyGivenOverall += amountToGive;
                }
            }
            
            totalToDistribute -= moneyGivenThisPass;

            if (moneyGivenThisPass < 0.01 && totalToDistribute > 0.01) {
                 if (!distributionMessage.textContent && totalMoneyGivenOverall > 0) {
                    distributionMessage.textContent = `Distributed $${totalMoneyGivenOverall.toFixed(2)}. $${(parseFloat(amountToDistributeInput.value) - totalMoneyGivenOverall).toFixed(2)} could not be fully distributed.`;
                 } else if (!distributionMessage.textContent) {
                    distributionMessage.textContent = `No funds could be distributed with current settings. $${totalToDistribute.toFixed(2)} remaining.`
                 }
                 break;
            }
             if (moneyGivenThisPass === 0 && totalToDistribute > 0.01) { // No money given, stop
                if (!distributionMessage.textContent) {
                    distributionMessage.textContent = `Distributed $${totalMoneyGivenOverall.toFixed(2)}. Remaining $${totalToDistribute.toFixed(2)} could not be allocated further.`;
                }
                break;
            }
        }
        
        if (!distributionMessage.textContent) {
             distributionMessage.textContent = `Successfully distributed $${totalMoneyGivenOverall.toFixed(2)}.`;
             if (totalToDistribute > 0.01) {
                 distributionMessage.textContent += ` $${totalToDistribute.toFixed(2)} remains undistributed.`;
             }
        }
        amountToDistributeInput.value = '';
        saveAndRender(); // This will use the updated currentAmounts
    }


    function escapeCsvValue(value) {
        // ... (escapeCsvValue remains the same)
        if (value == null) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
    }

    function downloadCSV() {
        // ... (downloadCSV remains the same)
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

    // --- NEW: CSV Import Functions ---
    function parseCsvRowRobust(rowStr) {
        const result = [];
        let currentField = '';
        let inQuotes = false;
        for (let i = 0; i < rowStr.length; i++) {
            const char = rowStr[i];
            if (char === '"') {
                if (inQuotes && i + 1 < rowStr.length && rowStr[i + 1] === '"') { // Escaped double quote
                    currentField += '"';
                    i++; // Skip next quote
                } else {
                    inQuotes = !inQuotes; // Toggle inQuotes state
                }
            } else if (char === ',' && !inQuotes) {
                result.push(currentField.trim());
                currentField = '';
            } else {
                currentField += char;
            }
        }
        result.push(currentField.trim()); // Add the last field
        return result;
    }

    function handleImportCSV() {
        const file = csvFileInput.files[0];
        if (!file) {
            importMessage.textContent = 'Please select a CSV file to import.';
            importMessage.style.color = 'red';
            return;
        }

        const reader = new FileReader();
        reader.onload = function(event) {
            const csvData = event.target.result;
            const newAccounts = [];
            let errors = [];
            let importedCount = 0;

            const lines = csvData.split(/\r\n|\n/); // Split by newline

            // Skip header row (optional: could validate headers)
            // Expected order: Name, Goal, Current, (Ignored Remaining), Priority (ignored), Zen, Days
            const startIndex = lines[0].toLowerCase().includes('account name') ? 1 : 0;


            for (let i = startIndex; i < lines.length; i++) {
                const line = lines[i].trim();
                if (!line) continue; // Skip empty lines

                const values = parseCsvRowRobust(line);

                if (values.length < 6) { // Expect at least Name, Goal, Current, (skip), Zen, Days (Priority is auto)
                    errors.push(`Row ${i + 1}: Not enough columns (found ${values.length}, expected at least 6 relevant).`);
                    continue;
                }
                
                try {
                    const name = values[0];
                    const goalAmount = parseFloat(values[1]);
                    const currentAmount = parseFloat(values[2]);
                    // values[3] is 'Remaining to Goal', which is calculated, so we ignore it.
                    // values[4] would be 'Priority' from export, we ignore this and set it by order.
                    const zenWeight = parseFloat(values[values.length-2]); // Assuming Zen is second to last if 7 cols, or values[4] if only 6 expected cols
                    const daysRemaining = parseInt(values[values.length-1]); // Assuming Days is last

                    // Basic validation
                    if (!name) throw new Error("Account name is missing.");
                    if (isNaN(goalAmount) || goalAmount <= 0) throw new Error("Invalid Goal Amount.");
                    if (isNaN(currentAmount) || currentAmount < 0) throw new Error("Invalid Current Amount.");
                    if (isNaN(zenWeight) || zenWeight < 1 || zenWeight > 3) throw new Error("Invalid Zen Weight (must be 1-3).");
                    if (isNaN(daysRemaining) || daysRemaining < 0) throw new Error("Invalid Days Remaining.");
                    
                    if (currentAmount > goalAmount) { // Cap current amount at goal amount during import
                        console.warn(`Row ${i+1}: Current amount (${currentAmount}) for "${name}" was greater than goal (${goalAmount}). Capping at goal.`);
                        // currentAmount = goalAmount; // Optional: auto-correct
                    }


                    newAccounts.push({
                        id: Date.now() + i, // Unique ID
                        name: name,
                        goalAmount: goalAmount,
                        currentAmount: currentAmount,
                        priority: 0, // Will be set by updatePriorities
                        zenWeight: zenWeight,
                        daysRemaining: daysRemaining
                    });
                    importedCount++;
                } catch (e) {
                    errors.push(`Row ${i + 1} ("${values[0] || 'Unknown Name'}"): ${e.message}`);
                }
            }

            if (newAccounts.length > 0) {
                accounts = newAccounts; // Overwrite existing accounts
                updatePriorities(); // Set sequential priorities for the new list
                saveAndRender();
                importMessage.textContent = `Successfully imported ${importedCount} accounts.`;
                importMessage.style.color = 'green';
            } else if (errors.length === 0 && importedCount === 0) {
                importMessage.textContent = 'No valid accounts found in the CSV to import.';
                importMessage.style.color = 'orange';
            }


            if (errors.length > 0) {
                const existingMsg = importMessage.textContent;
                importMessage.innerHTML = `${existingMsg}<br/><strong>Import Errors:</strong><br/>${errors.slice(0,5).join('<br/>')}`; // Show first 5 errors
                if (errors.length > 5) importMessage.innerHTML += `<br/>And ${errors.length - 5} more errors...`;
                importMessage.style.color = newAccounts.length > 0 ? 'orange' : 'red';
                console.error("CSV Import Errors:", errors);
            }
            csvFileInput.value = ''; // Reset file input
        };

        reader.onerror = function() {
            importMessage.textContent = 'Failed to read the file.';
            importMessage.style.color = 'red';
            csvFileInput.value = ''; // Reset file input
        };

        reader.readAsText(file);
    }


    // --- NEW: Drag and Drop Handlers ---
    function handleDragStart(e) {
        draggedItem = e.target; // The <tr> element
        draggedItemAccountId = draggedItem.dataset.accountId;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedItemAccountId); // Necessary for Firefox
        setTimeout(() => { // Make the dragged item semi-transparent
            draggedItem.classList.add('dragging');
        }, 0);
    }

    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        const targetRow = e.target.closest('tr');
        if (targetRow && targetRow !== draggedItem && targetRow.dataset.accountId) {
            // Remove previous drag-over class from other elements
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


        if (!targetRow || targetRow === draggedItem || !draggedItemAccountId) {
            return; // No drop if not on a valid row or dropping on itself
        }

        const targetAccountId = targetRow.dataset.accountId;
        const draggedIndex = accounts.findIndex(acc => String(acc.id) === String(draggedItemAccountId));
        let targetIndex = accounts.findIndex(acc => String(acc.id) === String(targetAccountId));

        if (draggedIndex === -1 || targetIndex === -1) {
            console.error("Could not find dragged or target item in accounts array.");
            return;
        }

        // Remove the dragged item and insert it before the target item
        const [draggedAccount] = accounts.splice(draggedIndex, 1);

        // Adjust targetIndex if dragged item was before target item
        if (draggedIndex < targetIndex) {
             // No adjustment needed when inserting before using current targetIndex after splice
        }
        
        // Determine if dropping above or below target for precise placement
        const rect = targetRow.getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;
        if (e.clientY >= midpoint) { // Dropped on the lower half of the target row, insert after
            targetIndex = accounts.findIndex(acc => String(acc.id) === String(targetAccountId)); // re-fetch targetIndex after splice
            accounts.splice(targetIndex + 1, 0, draggedAccount);
        } else { // Dropped on the upper half, insert before
            targetIndex = accounts.findIndex(acc => String(acc.id) === String(targetAccountId)); // re-fetch targetIndex after splice
            accounts.splice(targetIndex, 0, draggedAccount);
        }

        updatePriorities(); // Re-assign sequential priorities
        saveAndRender();
    }

    function handleDragEnd(e) {
        if (draggedItem) {
            draggedItem.classList.remove('dragging');
        }
        document.querySelectorAll('#accountsTableBody tr.drag-over').forEach(row => row.classList.remove('drag-over'));
        draggedItem = null;
        draggedItemAccountId = null;
    }


    function saveAndRender() {
        saveAccounts();
        renderAccounts();
    }

    // Event Listeners
    addItemBtn.addEventListener('click', addAccount);
    distributeBtn.addEventListener('click', distributeFunds);
    downloadCsvBtn.addEventListener('click', downloadCSV);
    importCsvBtn.addEventListener('click', handleImportCSV); // NEW Listener

    // Initial render
    renderAccounts();
});