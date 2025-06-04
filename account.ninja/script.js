document.addEventListener('DOMContentLoaded', () => {
    const addItemBtn = document.getElementById('addItemBtn');
    const accountNameInput = document.getElementById('accountName');
    const goalAmountInput = document.getElementById('goalAmount');
    const priorityInput = document.getElementById('priority');
    const zenWeightInput = document.getElementById('zenWeight');
    const daysRemainingInput = document.getElementById('daysRemaining');
    const accountsTableBody = document.getElementById('accountsTableBody');
    const amountToDistributeInput = document.getElementById('amountToDistribute');
    const distributeBtn = document.getElementById('distributeBtn');
    const distributionMessage = document.getElementById('distributionMessage');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn'); // NEW: Get reference to new button

    let accounts = JSON.parse(localStorage.getItem('accountsNinjaDB')) || [];

    function saveAccounts() {
        localStorage.setItem('accountsNinjaDB', JSON.stringify(accounts));
    }

    function renderAccounts() {
        accountsTableBody.innerHTML = ''; // Clear existing rows
        if (accounts.length === 0) {
            const row = accountsTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 8;
            cell.textContent = 'No accounts yet. Add some!';
            cell.style.textAlign = 'center';
            return;
        }

        accounts.forEach((account, index) => {
            const row = accountsTableBody.insertRow();
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
                    saveAndRender();
                } else {
                    currentAmountInput.value = account.currentAmount.toFixed(2); // revert if invalid
                }
            });
            currentAmountCell.appendChild(currentAmountInput);

            row.insertCell().textContent = `$${Math.max(0, account.goalAmount - account.currentAmount).toFixed(2)}`;

            const priorityCell = row.insertCell();
            const priorityValueInput = document.createElement('input');
            priorityValueInput.type = 'number';
            priorityValueInput.value = account.priority;
            priorityValueInput.min = 1;
            priorityValueInput.addEventListener('change', () => {
                const newValue = parseInt(priorityValueInput.value);
                if (!isNaN(newValue) && newValue >= 1) {
                    account.priority = newValue;
                    saveAndRender();
                } else {
                    priorityValueInput.value = account.priority;
                }
            });
            priorityCell.appendChild(priorityValueInput);


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
                accounts.splice(index, 1);
                saveAndRender();
            });
            actionsCell.appendChild(deleteBtn);
        });
    }

    function addAccount() {
        const name = accountNameInput.value.trim();
        const goalAmount = parseFloat(goalAmountInput.value);
        const priority = parseInt(priorityInput.value);
        const zenWeight = parseFloat(zenWeightInput.value);
        const daysRemaining = parseInt(daysRemainingInput.value);

        if (!name || isNaN(goalAmount) || isNaN(priority) || isNaN(zenWeight) || isNaN(daysRemaining)) {
            alert('Please fill in all fields with valid numbers.');
            return;
        }
        if (goalAmount <= 0 || priority <= 0 || zenWeight < 1 || zenWeight > 3 || daysRemaining < 0) {
            alert('Please enter valid values (Goal > 0, Priority > 0, Zen 1-3, Days >= 0).');
            return;
        }

        accounts.push({
            id: Date.now(), // Simple unique ID
            name,
            goalAmount,
            currentAmount: 0,
            priority,
            zenWeight,
            daysRemaining
        });

        accountNameInput.value = '';
        goalAmountInput.value = '';
        priorityInput.value = '';
        zenWeightInput.value = '';
        daysRemainingInput.value = '';

        saveAndRender();
    }

    function distributeFunds() {
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

        while (totalToDistribute > 0.01 && iterations < maxIterations) {
            iterations++;
            let eligibleAccounts = accounts.filter(acc => acc.currentAmount < acc.goalAmount);
            if (eligibleAccounts.length === 0) {
                distributionMessage.textContent = `No accounts need funding. $${totalToDistribute.toFixed(2)} remaining.`;
                break;
            }

            let totalCalculatedWeight = 0;
            eligibleAccounts.forEach(acc => {
                const priorityValue = acc.priority;
                const zenValue = acc.zenWeight;
                const urgencyValue = 1 / (acc.daysRemaining + 0.001);
                acc.calculatedWeight = (zenValue * urgencyValue) / priorityValue;
                totalCalculatedWeight += acc.calculatedWeight;
            });

            if (totalCalculatedWeight === 0) {
                 distributionMessage.textContent = `Could not determine weights for distribution. $${totalToDistribute.toFixed(2)} remaining.`;
                break;
            }

            let moneyGivenThisPass = 0;
            for (const acc of eligibleAccounts) {
                const needed = acc.goalAmount - acc.currentAmount;
                if (needed <= 0) continue;

                const proportionalShare = (acc.calculatedWeight / totalCalculatedWeight) * totalToDistribute;
                const amountToGive = Math.min(proportionalShare, needed);

                if (amountToGive > 0) {
                    acc.currentAmount += amountToGive;
                    moneyGivenThisPass += amountToGive;
                    totalMoneyGivenOverall += amountToGive;
                }
            }

            if (moneyGivenThisPass < 0.01 && totalToDistribute > 0.01) {
                 if (!distributionMessage.textContent) {
                    distributionMessage.textContent = `Distributed $${totalMoneyGivenOverall.toFixed(2)}. $${(parseFloat(amountToDistributeInput.value) - totalMoneyGivenOverall).toFixed(2)} could not be fully distributed due to small remaining needs or rounding.`;
                 }
                 break;
            }

            totalToDistribute -= moneyGivenThisPass;

            if (moneyGivenThisPass === 0 && totalToDistribute > 0.01) {
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
        saveAndRender();
    }

    // NEW: Function to escape CSV data
    function escapeCsvValue(value) {
        if (value == null) return ''; // Handle null or undefined by returning an empty string
        const stringValue = String(value);
        // If the value contains a comma, double quote, or newline, wrap it in double quotes
        // and escape any existing double quotes by doubling them.
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
    }

    // NEW: Function to download data as CSV
    function downloadCSV() {
        if (accounts.length === 0) {
            alert('No accounts to download.');
            return;
        }

        const headers = [
            'Account Name',
            'Goal Amount ($)',
            'Current Amount ($)',
            'Remaining to Goal ($)',
            'Priority',
            'Zen Weight (1-3)',
            'Days Remaining'
        ];

        let csvContent = headers.join(',') + '\n'; // Add header row

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
        if (link.download !== undefined) { // Feature detection
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', 'account_ninja_export.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url); // Clean up
        } else {
            alert('CSV download is not supported by your browser.');
        }
    }

    function saveAndRender() {
        saveAccounts();
        renderAccounts();
    }

    addItemBtn.addEventListener('click', addAccount);
    distributeBtn.addEventListener('click', distributeFunds);
    downloadCsvBtn.addEventListener('click', downloadCSV); // NEW: Add event listener for CSV download

    // Initial render
    renderAccounts();
});