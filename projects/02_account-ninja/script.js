document.addEventListener('DOMContentLoaded', () => {
    // --- 1. DOM Element References ---
    const addItemBtn = document.getElementById('addItemBtn');
    const accountNameInput = document.getElementById('accountName');
    const goalAmountInput = document.getElementById('goalAmount');
    const priorityInput = document.getElementById('priority');
    const zenWeightInput = document.getElementById('zenWeight');
    const daysRemainingInput = document.getElementById('daysRemaining');
    const accountsTableBody = document.getElementById('accountsTableBody');
    const amountToDistributeInput = document.getElementById('amountToDistribute');
    const distributionCyclesInput = document.getElementById('distributionCyclesInput');
    const distributeBtn = document.getElementById('distributeBtn');
    const distributionMessage = document.getElementById('distributionMessage');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');
    const downloadTimelineBtn = document.getElementById('downloadTimelineBtn');
    const csvFileInput = document.getElementById('csvFileInput');
    const importCsvBtn = document.getElementById('importCsvBtn');
    const importMessage = document.getElementById('importMessage');

    // --- 2. Global-like variables ---
    let accounts = JSON.parse(localStorage.getItem('accountsNinjaDB')) || [];
    let draggedItem = null;
    let draggedItemAccountId = null;

    // --- 3. Core Data & Utility Functions ---
    function saveAccounts() {
        localStorage.setItem('accountsNinjaDB', JSON.stringify(accounts));
    }

    function updatePriorities() {
        accounts.forEach((account, index) => {
            account.priority = index + 1;
        });
    }

    function saveAndRender() {
        saveAccounts();
        renderAccounts();
    }

    // --- 4. Rendering Function ---
    function renderAccounts() {
        accountsTableBody.innerHTML = '';
        if (accounts.length === 0) {
            const row = accountsTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 8;
            cell.textContent = 'No accounts yet. Add some!';
            cell.style.textAlign = 'center';
            return;
        }

        accounts.forEach((account) => {
            const row = accountsTableBody.insertRow();
            row.dataset.accountId = account.id;
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
                    saveAndRender(); 
                } else {
                    currentAmountInput.value = account.currentAmount.toFixed(2);
                }
            });
            currentAmountCell.appendChild(currentAmountInput);

            row.insertCell().textContent = `$${Math.max(0, account.goalAmount - account.currentAmount).toFixed(2)}`;
            row.insertCell().textContent = account.priority;

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
                updatePriorities();
                saveAndRender();
            });
            actionsCell.appendChild(deleteBtn);
        });
    }

    // --- 5. Feature Functions ---

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
            id: Date.now() + Math.random(),
            name,
            goalAmount,
            currentAmount: 0,
            priority: 0,
            zenWeight,
            daysRemaining
        });
        updatePriorities();
        [accountNameInput, goalAmountInput, priorityInput, zenWeightInput, daysRemainingInput].forEach(input => input.value = '');
        saveAndRender();
    }

    function runSingleDistributionCycle(accountsToProcess, amountForCycle, isTimelineSimulation = false) {
        let moneyGivenInThisCycle = 0;
        const maxIterations = 10;
        let iterations = 0;
        let currentAmountToDistribute = amountForCycle;

        while (currentAmountToDistribute > 0.01 && iterations < maxIterations) {
            iterations++;
            let moneyGivenThisPass = 0;
            let eligibleAccounts = accountsToProcess.filter(acc => {
                const needsFunds = acc.currentAmount < acc.goalAmount;
                if (isTimelineSimulation) {
                    return needsFunds && acc.daysRemaining > 0;
                }
                return needsFunds;
            });
            
            if (eligibleAccounts.length === 0) break;

            let totalCalculatedWeight = 0;
            eligibleAccounts.forEach(acc => {
                acc.calculatedWeight = (acc.zenWeight * (1 / (acc.daysRemaining + 0.001))) / acc.priority;
                totalCalculatedWeight += acc.calculatedWeight;
            });

            if (totalCalculatedWeight === 0) break;

            for (const acc of eligibleAccounts) {
                const needed = acc.goalAmount - acc.currentAmount;
                if (needed <= 0) continue;
                const proportionalShare = (acc.calculatedWeight / totalCalculatedWeight) * currentAmountToDistribute;
                const amountToGive = Math.min(proportionalShare, needed);
                if (amountToGive > 0.009) {
                    acc.currentAmount += amountToGive;
                    moneyGivenThisPass += amountToGive;
                }
            }
            
            if (moneyGivenThisPass < 0.01) break;
            currentAmountToDistribute -= moneyGivenThisPass;
            moneyGivenInThisCycle += moneyGivenThisPass;
        }
        return moneyGivenInThisCycle;
    }

    function distributeFunds() {
        const amountPerCycle = parseFloat(amountToDistributeInput.value);
        const numCyclesRequested = parseInt(distributionCyclesInput.value) || 1;
        if (isNaN(amountPerCycle) || amountPerCycle <= 0 || numCyclesRequested < 1) {
            distributionMessage.textContent = 'Please enter a valid Amount per Cycle and at least 1 Cycle.';
            distributionMessage.style.color = 'red';
            return;
        }

        distributionMessage.textContent = '';
        let grandTotalDistributed = 0;
        let cycleReport = [];
        let actualCyclesProcessed = 0;

        for (let cycle = 1; cycle <= numCyclesRequested; cycle++) {
            actualCyclesProcessed = cycle;
            const moneyGivenInThisCycle = runSingleDistributionCycle(accounts, amountPerCycle, false);
            grandTotalDistributed += moneyGivenInThisCycle;
            
            let cycleMessage = `Cycle ${cycle}: Actually distributed $${moneyGivenInThisCycle.toFixed(2)}.`;
            cycleReport.push(cycleMessage);

            if (moneyGivenInThisCycle < amountPerCycle) {
                const anyAccountNeedsFunding = accounts.some(acc => acc.currentAmount < acc.goalAmount);
                if (!anyAccountNeedsFunding) {
                    cycleReport.push(`--- All accounts appear to be full. Stopping further cycles. ---`);
                    break;
                } else if (moneyGivenInThisCycle < 0.01) {
                    cycleReport.push(`--- Cycle distributed very little. Stopping further cycles. ---`);
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
        
        saveAndRender();
    }

    // UPDATED: generateTimelineCSV now includes the initial state (Cycle 0)
    function generateTimelineCSV() {
        const amountPerCycle = parseFloat(amountToDistributeInput.value);
        const numCyclesToSimulate = parseInt(distributionCyclesInput.value) || 1;
        if (isNaN(amountPerCycle) || amountPerCycle <= 0 || numCyclesToSimulate < 1) {
            alert('Please enter a valid "Amount per Cycle" and "Cycles" to run the simulation.');
            return;
        }

        const simAccounts = JSON.parse(JSON.stringify(accounts));
        
        const headers = ['Cycle', 'Account Name', 'Goal Amount ($)', 'Current Amount ($)', 'Remaining to Goal ($)', 'Priority', 'Zen Weight (1-3)', 'Days Remaining'];
        const csvRows = [headers];

        // NEW: Add the initial state of accounts as Cycle 0
        simAccounts.forEach(acc => {
            const remaining = Math.max(0, acc.goalAmount - acc.currentAmount);
            const row = [
                0, // Cycle 0 represents the initial state before simulation
                acc.name,
                acc.goalAmount.toFixed(2),
                acc.currentAmount.toFixed(2),
                remaining.toFixed(2),
                acc.priority,
                acc.zenWeight,
                acc.daysRemaining
            ];
            csvRows.push(row);
        });

        // Main simulation loop starts from Cycle 1
        for (let cycle = 1; cycle <= numCyclesToSimulate; cycle++) {
            runSingleDistributionCycle(simAccounts, amountPerCycle, true);

            simAccounts.forEach(acc => {
                acc.daysRemaining = Math.max(0, acc.daysRemaining - 30);
            });

            simAccounts.forEach(acc => {
                const remaining = Math.max(0, acc.goalAmount - acc.currentAmount);
                const row = [cycle, acc.name, acc.goalAmount.toFixed(2), acc.currentAmount.toFixed(2), remaining.toFixed(2), acc.priority, acc.zenWeight, acc.daysRemaining];
                csvRows.push(row);
            });

            const allFunded = simAccounts.every(acc => acc.currentAmount >= acc.goalAmount);
            const allOutOfTime = simAccounts.every(acc => acc.daysRemaining <= 0 || acc.currentAmount >= acc.goalAmount);
            if (allFunded || allOutOfTime) {
                break;
            }
        }

        let csvContent = csvRows.map(row => row.map(escapeCsvValue).join(',')).join('\n');
        downloadCsvContent(csvContent, 'account_ninja_timeline.csv');
    }

    // --- 6. Helper & Existing Feature Functions ---
    function downloadCsvContent(csvContent, fileName) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', fileName);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } else {
            alert('CSV download is not supported by your browser.');
        }
    }

    function downloadCSV() {
        if (accounts.length === 0) {
            alert('No accounts to download.');
            return;
        }
        let csvContent = accounts.map(account => [
            escapeCsvValue(account.name),
            escapeCsvValue(account.goalAmount.toFixed(2)),
            escapeCsvValue(account.currentAmount.toFixed(2)),
            escapeCsvValue(Math.max(0, account.goalAmount - account.currentAmount).toFixed(2)),
            escapeCsvValue(account.priority),
            escapeCsvValue(account.zenWeight),
            escapeCsvValue(account.daysRemaining)
        ]);
        const headers = ['Account Name', 'Goal Amount ($)', 'Current Amount ($)', 'Remaining to Goal ($)', 'Priority', 'Zen Weight (1-3)', 'Days Remaining'];
        csvContent.unshift(headers);
        downloadCsvContent(csvContent.map(row => row.join(',')).join('\n'), 'account_ninja_snapshot.csv');
    }

    function handleImportCSV() {
        const file = csvFileInput.files[0];
        if (!file) {
            importMessage.textContent = 'Please select a CSV file.'; return;
        }
        importMessage.textContent = 'Processing...';
        const reader = new FileReader();
        reader.onload = function(event) {
            const csvData = event.target.result;
            const newAccounts = [];
            let errors = [];
            let importedCount = 0;
            const lines = csvData.split(/\r\n|\n/);
            const startIndex = lines[0].toLowerCase().includes('account name') ? 1 : 0;
            for (let i = startIndex; i < lines.length; i++) {
                const line = lines[i].trim();
                if (!line) continue;
                const values = parseCsvRowRobust(line);
                if (values.length < 5) {
                    errors.push(`Row ${i + 1}: Not enough columns.`); continue;
                }
                try {
                    let zenWeight, daysRemaining;
                    if (values.length >= 7) {
                        zenWeight = parseFloat(values[5]);
                        daysRemaining = parseInt(values[6]);
                    } else if (values.length >= 5) {
                         zenWeight = parseFloat(values[3]);
                         daysRemaining = parseInt(values[4]);
                    } else { throw new Error("Not enough columns for Zen and Days."); }

                    const name = values[0];
                    const goalAmount = parseFloat(values[1]);
                    const currentAmount = parseFloat(values[2]);
                    if (!name) throw new Error("Account name is missing.");
                    if (isNaN(goalAmount) || goalAmount <= 0) throw new Error("Invalid Goal Amount.");
                    if (isNaN(currentAmount) || currentAmount < 0) throw new Error("Invalid Current Amount.");
                    if (isNaN(zenWeight) || zenWeight < 1 || zenWeight > 3) throw new Error("Invalid Zen Weight (must be 1-3).");
                    if (isNaN(daysRemaining) || daysRemaining < 0) throw new Error("Invalid Days Remaining.");
                    newAccounts.push({
                        id: Date.now() + i + Math.random(), name, goalAmount, currentAmount, priority: 0, zenWeight, daysRemaining
                    });
                    importedCount++;
                } catch (e) {
                    errors.push(`Row ${i + 1} ("${values[0] || ''}"): ${e.message}`);
                }
            }
            if (newAccounts.length > 0) {
                accounts = newAccounts; updatePriorities(); saveAndRender();
                importMessage.textContent = `Successfully imported ${importedCount} accounts.`; importMessage.style.color = 'green';
            } else if (errors.length === 0 && importedCount === 0) {
                importMessage.textContent = 'No valid accounts found in CSV.'; importMessage.style.color = 'orange';
            }
            if (errors.length > 0) {
                const existingMsg = importMessage.textContent.startsWith('Success') ? importMessage.textContent + '<br/>' : '';
                importMessage.innerHTML = `${existingMsg}<strong>Import Errors:</strong><br/>${errors.slice(0,5).join('<br/>')}`;
                if (errors.length > 5) importMessage.innerHTML += `<br/>And ${errors.length - 5} more errors...`;
                importMessage.style.color = newAccounts.length > 0 ? 'orange' : 'red'; console.error("CSV Errors:", errors);
            }
            csvFileInput.value = '';
        };
        reader.onerror = function() { importMessage.textContent = 'Failed to read file.'; importMessage.style.color = 'red'; csvFileInput.value = ''; };
        reader.readAsText(file);
    }
    
    function handleDragStart(e) {
        draggedItem = e.target;
        draggedItemAccountId = draggedItem.dataset.accountId;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedItemAccountId);
        setTimeout(() => { if (draggedItem) draggedItem.classList.add('dragging'); }, 0);
    }
    function handleDragOver(e) {
        e.preventDefault(); e.dataTransfer.dropEffect = 'move';
        const targetRow = e.target.closest('tr');
        if (targetRow && targetRow !== draggedItem && targetRow.dataset.accountId) {
            document.querySelectorAll('#accountsTableBody tr.drag-over').forEach(row => row.classList.remove('drag-over'));
            targetRow.classList.add('drag-over');
        }
    }
    function handleDragLeave(e) { e.target.closest('tr')?.classList.remove('drag-over'); }
    function handleDrop(e) {
        e.preventDefault();
        const targetRow = e.target.closest('tr');
        document.querySelectorAll('#accountsTableBody tr.drag-over').forEach(row => row.classList.remove('drag-over'));
        if (!targetRow || !draggedItem || targetRow === draggedItem || !draggedItemAccountId) { return; }
        const draggedAccountIndex = accounts.findIndex(acc => String(acc.id) === String(draggedItemAccountId));
        if (draggedAccountIndex === -1) { return; }
        const [draggedAccountObject] = accounts.splice(draggedAccountIndex, 1);
        let targetAccountIndex = accounts.findIndex(acc => String(acc.id) === String(targetRow.dataset.accountId));
        if (targetAccountIndex === -1) { accounts.push(draggedAccountObject); } else {
            const rect = targetRow.getBoundingClientRect();
            if (e.clientY >= (rect.top + rect.height / 2)) {
                accounts.splice(targetAccountIndex + 1, 0, draggedAccountObject);
            } else {
                accounts.splice(targetAccountIndex, 0, draggedAccountObject);
            }
        }
        updatePriorities(); saveAndRender();
    }
    function handleDragEnd(e) {
        if (draggedItem) { draggedItem.classList.remove('dragging'); }
        document.querySelectorAll('#accountsTableBody tr.drag-over').forEach(row => row.classList.remove('drag-over'));
        draggedItem = null; draggedItemAccountId = null;
    }

    function escapeCsvValue(value) {
        if (value == null) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
    }
    function parseCsvRowRobust(rowStr) {
        const result = []; let currentField = ''; let inQuotes = false;
        for (let i = 0; i < rowStr.length; i++) {
            const char = rowStr[i];
            if (char === '"') {
                if (inQuotes && i + 1 < rowStr.length && rowStr[i + 1] === '"') { currentField += '"'; i++; } else { inQuotes = !inQuotes; }
            } else if (char === ',' && !inQuotes) { result.push(currentField.trim()); currentField = ''; } else { currentField += char; }
        }
        result.push(currentField.trim());
        return result;
    }

    // --- 7. Main Event Listeners ---
    addItemBtn.addEventListener('click', addAccount);
    distributeBtn.addEventListener('click', distributeFunds);
    downloadCsvBtn.addEventListener('click', downloadCSV);
    downloadTimelineBtn.addEventListener('click', generateTimelineCSV);
    importCsvBtn.addEventListener('click', handleImportCSV);

    // --- 8. Initial Setup ---
    updatePriorities();
    renderAccounts();
});