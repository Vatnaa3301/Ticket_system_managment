// GLOBAL TICKET DETAIL MODAL POPUP FUNCTION
window.openTicketDetailModal = async function(ticketId) {
    const targetModal = document.getElementById('ticketDetailModal');
    if (targetModal) {
        targetModal.style.display = 'flex';
        targetModal.classList.add('active');
    }

    try {
        const res = await fetch(`/api/tickets/${ticketId}/details/`);
        const json = await res.json();
        if (!json.success) return;

        const t = json.ticket;
        window._currentTicketData = t;
        window._currentTicketCanEdit = (t.can_edit !== false);

        if (document.getElementById('detailCode')) document.getElementById('detailCode').textContent = t.ticket_code;
        if (document.getElementById('detailSubject')) document.getElementById('detailSubject').textContent = t.subject;
        if (document.getElementById('detailDescription')) document.getElementById('detailDescription').textContent = t.description || 'No description provided.';
        
        if (document.getElementById('detailPriority')) document.getElementById('detailPriority').textContent = t.priority;
        if (document.getElementById('detailCategory')) document.getElementById('detailCategory').textContent = t.category;
        
        const assigneeEl = document.getElementById('detailAssignee');
        const assigneeAvatarEl = document.getElementById('detailAssigneeAvatar');
        if (assigneeEl) {
            assigneeEl.textContent = t.assignee || 'Unassigned';
            assigneeEl.title = t.assignee_email ? `${t.assignee} (${t.assignee_email})` : (t.assignee || 'Unassigned');
        }
        if (assigneeAvatarEl) {
            if (t.assignee_image) {
                assigneeAvatarEl.innerHTML = `<img src="${t.assignee_image}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
                assigneeAvatarEl.style.background = 'transparent';
                assigneeAvatarEl.style.overflow = 'hidden';
            } else if (t.assignee_initials) {
                assigneeAvatarEl.innerHTML = t.assignee_initials;
                assigneeAvatarEl.style.background = t.assignee_color || '#0052cc';
                assigneeAvatarEl.style.color = '#ffffff';
            } else {
                assigneeAvatarEl.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;
                assigneeAvatarEl.style.background = '#626f86';
                assigneeAvatarEl.style.color = '#ffffff';
            }
        }

        const creatorEl = document.getElementById('detailCreator');
        const creatorAvatarEl = document.getElementById('detailCreatorAvatar');
        if (creatorEl) {
            creatorEl.textContent = t.creator || 'Unknown';
            creatorEl.title = t.creator_email ? `${t.creator} (${t.creator_email})` : (t.creator || 'Unknown');
        }
        if (creatorAvatarEl) {
            if (t.creator_image) {
                creatorAvatarEl.innerHTML = `<img src="${t.creator_image}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
                creatorAvatarEl.style.background = 'transparent';
                creatorAvatarEl.style.overflow = 'hidden';
            } else if (t.creator_initials) {
                creatorAvatarEl.innerHTML = t.creator_initials;
                creatorAvatarEl.style.background = t.creator_color || '#0052cc';
                creatorAvatarEl.style.color = '#ffffff';
            } else {
                creatorAvatarEl.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;
                creatorAvatarEl.style.background = '#626f86';
                creatorAvatarEl.style.color = '#ffffff';
            }
        }

        if (document.getElementById('detailCreated')) document.getElementById('detailCreated').textContent = t.created_at;
        const dueDateEl = document.getElementById('detailDueDate');
        if (dueDateEl) {
            if (t.due_date) {
                const formattedDate = t.due_date_formatted || t.due_date;
                if (t.is_due_soon) {
                    dueDateEl.innerHTML = `<span style="display:inline-flex; align-items:center; gap:4px; color:#ff5630; font-weight:600;">
                        ${formattedDate}
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5630" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" title="Due within 1 day or overdue" style="flex-shrink:0;">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                    </span>`;
                } else {
                    dueDateEl.textContent = formattedDate;
                }
            } else {
                dueDateEl.textContent = 'None';
            }
        }
        if (document.getElementById('detailStartDate')) document.getElementById('detailStartDate').textContent = t.start_date_formatted || 'None';


        // Populate Status Selector in Right Sidebar
        const statusSelect = document.getElementById('detailStatusSelect');
        if (statusSelect) {
            statusSelect.disabled = (t.can_edit === false);
            statusSelect.innerHTML = `
                <option value="1" ${t.status_id == 1 ? 'selected' : ''}>To Do</option>
                <option value="2" ${t.status_id == 2 ? 'selected' : ''}>In Progress</option>
                <option value="3" ${t.status_id == 3 ? 'selected' : ''}>In Review</option>
                <option value="4" ${t.status_id == 4 ? 'selected' : ''}>Done</option>
            `;
            statusSelect.onchange = async () => {
                const newStatusId = statusSelect.value;
                try {
                    await fetch(`/api/tickets/${ticketId}/update-status/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ status_id: newStatusId })
                    });
                } catch (err) {
                    console.error(err);
                }
            };
        }

        // Store current attachments & render
        if (window.renderAttachments) {
            window.currentTicketAttachments = t.attachments || [];
            window.renderAttachments();
        }

        // Render threaded comments
        if (window.renderThreadedComments) {
            window.renderThreadedComments(t.comments || [], t.ticket_id);
        }


        // Initialize Pusher Real-Time Live Chat Channel
        if (typeof Pusher !== 'undefined') {
            if (window._currentPusherChannel) {
                window._currentPusherChannel.unbind_all();
                window._currentPusherChannel.unsubscribe();
            }
            if (!window._pusherClient) {
                window._pusherClient = new Pusher('308cbea8f43adedfd722', {
                    cluster: 'ap1'
                });
            }
            const channelName = `ticket_${ticketId}`;
            window._currentPusherChannel = window._pusherClient.subscribe(channelName);
            window._currentPusherChannel.bind('new-comment', function(data) {
                const commentList = document.getElementById('detailComments');
                if (!commentList) return;

                if (!window._currentTicketData) window._currentTicketData = { comments: [] };
                if (!window._currentTicketData.comments) window._currentTicketData.comments = [];

                const exists = window._currentTicketData.comments.some(c => String(c.id) === String(data.comment_id));
                if (!exists) {
                    window._currentTicketData.comments.push({
                        id: data.comment_id,
                        parent_id: data.parent_id || null,
                        user: data.user,
                        user_initials: data.user_initials || (data.user || 'PV').substring(0, 2).toUpperCase(),
                        user_avatar_color: data.user_avatar_color || '#0052cc',
                        user_profile_image: data.user_profile_image || '',
                        text: data.text,
                        is_internal: data.is_internal || false,
                        created_at: data.created_at
                    });
                }

                if (window.renderThreadedComments) {
                    window.renderThreadedComments(window._currentTicketData.comments, ticketId);
                }
            });

        }

        // Render History activity logs
        const historyLogsContainer = document.getElementById('detailHistoryLogs');
        if (historyLogsContainer) {
            historyLogsContainer.innerHTML = '';
            if (!t.logs || t.logs.length === 0) {
                historyLogsContainer.innerHTML = '<div style="font-size:12px; color:var(--jira-text-muted); padding:8px 0;">No history activity logs found.</div>';
            } else {
                t.logs.forEach(l => {
                    const item = document.createElement('div');
                    item.style.padding = '8px 0';
                    item.style.borderBottom = '1px solid var(--jira-border)';
                    item.style.fontSize = '12px';
                    item.innerHTML = `
                        <div style="color:var(--jira-text-muted); display:flex; justify-content:space-between;">
                            <strong>${l.user}</strong> <span>${l.created_at}</span>
                        </div>
                        <div style="color:var(--jira-text-dark); margin-top:2px;">
                            <strong>${l.action}:</strong> ${l.new_value}
                        </div>
                    `;
                    historyLogsContainer.appendChild(item);
                });
            }
        }

        // Store current ticket ID for comment submit
        const addCommBtn = document.getElementById('addCommentBtn');
        if (addCommBtn) addCommBtn.dataset.ticketId = ticketId;

    } catch (err) {
        console.error('Error fetching ticket details:', err);
    }
};

window.currentTicketAttachments = [];
window.currentAttFilter = 'all';

// THREADED / NESTED COMMENTS RENDERER (YOUTUBE STYLE)
window.renderThreadedComments = function(comments, ticketId) {
    const commentList = document.getElementById('detailComments');
    if (!commentList) return;
    commentList.innerHTML = '';

    if (!comments || comments.length === 0) {
        commentList.innerHTML = '<div style="font-size:12px; color:var(--jira-text-muted); padding:10px 0; text-align:center;">No comments yet.</div>';
        return;
    }

    const topLevel = [];
    const repliesMap = {};

    comments.forEach(c => {
        if (c.parent_id) {
            if (!repliesMap[c.parent_id]) repliesMap[c.parent_id] = [];
            repliesMap[c.parent_id].push(c);
        } else {
            topLevel.push(c);
        }
    });

    function createCommentNode(c, isReply = false) {
        const cDiv = document.createElement('div');
        cDiv.className = isReply ? 'comment-item comment-reply-item' : 'comment-item';
        cDiv.id = `comment-item-${c.id}`;
        cDiv.style.padding = '10px 0';
        if (!isReply) cDiv.style.borderBottom = '1px solid var(--jira-border)';

        const formattedContent = window.formatCommentText ? window.formatCommentText(c.text) : c.text;
        const userInitials = c.user_initials || (c.user || 'PV').substring(0, 2).toUpperCase();
        const avatarBg = c.user_avatar_color || '#0052cc';
        const avatarInner = c.user_profile_image 
            ? `<img src="${c.user_profile_image}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">` 
            : userInitials;

        cDiv.innerHTML = `
            <div style="display:flex; gap:10px;">
                <div class="user-avatar" style="width:28px; height:28px; font-size:10px; flex-shrink:0; background:${avatarBg}; color:#ffffff; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; overflow:hidden;">${avatarInner}</div>
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:12px; color:var(--jira-text-muted);">
                        <strong style="color:var(--jira-text-dark); font-size:13px;">${c.user}</strong>
                        <span>${c.created_at}</span>
                    </div>
                    <div style="font-size:13px; margin-top:4px; color:var(--jira-text-dark); line-height:1.5;">${formattedContent}</div>
                    
                    <div style="margin-top:4px; display:flex; align-items:center; gap:12px;">
                        <button type="button" class="btn-reply-comment" onclick="toggleInlineReplyForm(${c.id}, '${c.user}', ${ticketId})">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 17 4 12 9 7"/><path d="M20 18v-2a4 4 0 0 0-4-4H4"/></svg>
                            <span>Reply</span>
                        </button>
                    </div>

                    <div id="inlineReplyFormContainer-${c.id}" style="display:none;"></div>
                </div>
            </div>
        `;

        const childReplies = repliesMap[c.id];
        if (childReplies && childReplies.length > 0) {
            const threadContainer = document.createElement('div');
            threadContainer.className = 'comment-thread-container';

            childReplies.forEach(reply => {
                const replyNode = createCommentNode(reply, true);
                threadContainer.appendChild(replyNode);
            });

            cDiv.querySelector('div[style*="flex:1"]').appendChild(threadContainer);
        }

        return cDiv;
    }

    topLevel.forEach(c => {
        const node = createCommentNode(c, false);
        commentList.appendChild(node);
    });
};

window.toggleInlineReplyForm = function(commentId, authorName, ticketId) {
    const container = document.getElementById(`inlineReplyFormContainer-${commentId}`);
    if (!container) return;

    if (container.style.display === 'block') {
        container.style.display = 'none';
        container.innerHTML = '';
        return;
    }

    container.style.display = 'block';
    container.innerHTML = `
        <div class="inline-reply-box">
            <textarea id="replyInput-${commentId}" class="form-control" rows="2" style="background:#28282c; border:1px solid #38383e; color:#cecfd2; font-size:13px; resize:vertical; width:100%; border-radius:4px; padding:8px;" placeholder="Replying to @${authorName}..."></textarea>
            <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:8px;">
                <button type="button" class="btn-secondary" onclick="toggleInlineReplyForm(${commentId}, '${authorName}', ${ticketId})" style="padding:4px 12px; font-size:12px;">Cancel</button>
                <button type="button" class="btn-primary" onclick="submitInlineReply(${commentId}, ${ticketId})" style="padding:4px 14px; font-size:12px; background:#0052cc;">Reply</button>
            </div>
        </div>
    `;

    const input = document.getElementById(`replyInput-${commentId}`);
    if (input) input.focus();
};

window.submitInlineReply = async function(commentId, ticketId) {
    const input = document.getElementById(`replyInput-${commentId}`);
    const text = input ? input.value.trim() : '';
    if (!text) return;

    try {
        const res = await fetch(`/api/tickets/${ticketId}/comments/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                comment_text: text,
                parent_id: commentId
            })
        });
        const data = await res.json();
        if (data.success) {
            window.openTicketDetailModal(ticketId);
        } else {
            alert(data.error || 'Failed to submit reply.');
        }
    } catch (err) {
        console.error(err);
    }
};


window.renderAttachments = function() {
    const listEl = document.getElementById('detailAttachmentsList');
    const countEl = document.getElementById('detailAttachmentCount');
    if (!listEl) return;

    listEl.innerHTML = '';
    const filtered = window.currentTicketAttachments.filter(a => {
        if (window.currentAttFilter === 'all') return true;
        return a.category_type === window.currentAttFilter;
    });

    if (countEl) countEl.textContent = window.currentTicketAttachments.length;

    if (filtered.length === 0) {
        listEl.innerHTML = `<div style="font-size:12px; color:var(--jira-text-muted); padding:10px 0; text-align:center;">No attachments uploaded for this ticket.</div>`;
        return;
    }

    filtered.forEach(a => {
        const row = document.createElement('div');
        row.className = 'attachment-row';
        
        let iconOrThumb = '';
        if (a.is_image) {
            iconOrThumb = `<img src="${a.file_url}" class="att-thumb-box" alt="${a.file_name}" onclick="window.open('${a.file_url}', '_blank')" style="cursor:pointer;" title="Click to view full size">`;
        } else if (a.category_type === 'documents') {
            iconOrThumb = `<div class="att-thumb-box" style="color:var(--jira-blue);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div>`;
        } else if (a.category_type === 'videos') {
            iconOrThumb = `<div class="att-thumb-box" style="color:#eab308;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg></div>`;
        } else {
            iconOrThumb = `<div class="att-thumb-box" style="color:var(--jira-text-muted);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg></div>`;
        }

        row.innerHTML = `
            <div style="display:flex; align-items:center; gap:12px; overflow:hidden;">
                ${iconOrThumb}
                <div style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                    <a href="${a.file_url}" target="_blank" style="font-weight:600; color:var(--jira-blue); text-decoration:none; font-size:13px;" title="${a.file_name}">${a.file_name}</a>
                    <div style="font-size:11px; color:var(--jira-text-muted); margin-top:2px;">Added ${a.uploaded_at} by ${a.uploaded_by} • ${a.file_size}</div>
                </div>
            </div>
            <a href="${a.file_url}" download target="_blank" style="color:var(--jira-blue); padding:4px 8px; text-decoration:none; font-size:12px; font-weight:600; background:var(--jira-column-bg); border:1px solid var(--jira-border); border-radius:4px; display:inline-flex; align-items:center; gap:4px;" title="Download File"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Download</a>
        `;
        listEl.appendChild(row);
    });
};

// ---------------- DARK / LIGHT THEME TOGGLE ----------------
(function initJiraThemeToggle() {
    const activeTheme = localStorage.getItem('jira_theme') || 'dark';
    if (typeof window.applyJiraTheme === 'function') {
        window.applyJiraTheme(activeTheme);
    } else {
        document.documentElement.setAttribute('data-theme', activeTheme);
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    // ---------------- RESIZABLE SIDEBAR LOGIC ----------------




    // ---------------- DRAG AND DROP KANBAN CARDS ----------------
    const cards = document.querySelectorAll('.ticket-card');
    const columns = document.querySelectorAll('.column-cards-container');

    cards.forEach(card => {
        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', card.dataset.ticketId);
            card.classList.add('dragging');
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });

        // Click to view ticket details modal
        card.addEventListener('click', (e) => {
            if (e.target.closest('.no-modal')) return;
            window.openTicketDetailModal(card.dataset.ticketId);
        });
    });

    columns.forEach(column => {
        column.addEventListener('dragover', (e) => {
            e.preventDefault();
            column.classList.add('drag-over');
        });

        column.addEventListener('dragleave', () => {
            column.classList.remove('drag-over');
        });

        column.addEventListener('drop', async (e) => {
            e.preventDefault();
            column.classList.remove('drag-over');
            const ticketId = e.dataTransfer.getData('text/plain');
            const newStatusId = column.dataset.statusId;
            const card = document.querySelector(`.ticket-card[data-ticket-id="${ticketId}"]`);

            if (card && column) {
                column.appendChild(card);
                updateTicketStatus(ticketId, newStatusId);
                if (window.updateCardStatusIcon) window.updateCardStatusIcon(card, newStatusId);
                updateColumnCounts();
            }
        });
    });

    function updateCardStatusIcon(card, statusId) {
        if (!card) return;
        const keyIconBox = card.querySelector('.key-icon-box');
        if (!keyIconBox) return;

        let isDone = false;
        if (statusId) {
            const targetColumn = document.querySelector(`.column-cards-container[data-status-id="${statusId}"]`);
            const headerName = targetColumn ? targetColumn.closest('.kanban-column')?.querySelector('.column-header span:first-child')?.textContent?.trim() : '';
            if (headerName) {
                const lower = headerName.toLowerCase();
                isDone = (lower === 'done' || lower === 'closed' || lower === 'resolved');
            }
        } else {
            const cardCol = card.closest('.column-cards-container');
            const headerName = cardCol ? cardCol.closest('.kanban-column')?.querySelector('.column-header span:first-child')?.textContent?.trim() : '';
            if (headerName) {
                const lower = headerName.toLowerCase();
                isDone = (lower === 'done' || lower === 'closed' || lower === 'resolved');
            }
        }

        if (isDone) {
            keyIconBox.className = 'key-icon-box key-icon-green';
            keyIconBox.title = 'Done';
            keyIconBox.innerHTML = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
        } else {
            keyIconBox.className = 'key-icon-box key-icon-blue';
            keyIconBox.title = 'Task';
            keyIconBox.innerHTML = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>`;
        }
    }
    window.updateCardStatusIcon = updateCardStatusIcon;

    // Initialize status icons for all cards on board load
    document.querySelectorAll('.ticket-card').forEach(card => {
        updateCardStatusIcon(card);
    });

    function updateColumnCounts() {
        document.querySelectorAll('.kanban-column').forEach(col => {
            const countBadge = col.querySelector('.column-count');
            const cardCount = col.querySelectorAll('.ticket-card').length;
            if (countBadge) countBadge.textContent = cardCount;
        });
    }
    window.updateColumnCounts = updateColumnCounts;

    async function updateTicketStatus(ticketId, statusId) {
        try {
            const res = await fetch(`/api/tickets/${ticketId}/update-status/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status_id: statusId })
            });
            const data = await res.json();
            if (!data.success) {
                alert('Failed to update status: ' + data.error);
            }
        } catch (err) {
            console.error(err);
        }
    }

    // ---------------- MODAL OPEN / CLOSE LOGIC ----------------
    const createModal = document.getElementById('createTicketModal');
    const detailModal = document.getElementById('ticketDetailModal');

    document.querySelectorAll('.btn-open-create-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            const defaultStatus = btn.dataset.statusId;
            if (defaultStatus && document.getElementById('createStatus')) {
                document.getElementById('createStatus').value = defaultStatus;
            }
            if (createModal) {
                createModal.classList.add('active');
                createModal.style.display = 'flex';
            }
        });
    });

    // Close buttons logic for all modal dialogs
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-close-modal') || e.target.closest('.btn-close-modal')) {
            if (createModal) { createModal.classList.remove('active'); createModal.style.display = 'none'; }
            if (detailModal) { detailModal.classList.remove('active'); detailModal.style.display = 'none'; }
        }
        if (e.target === createModal) {
            createModal.classList.remove('active');
            createModal.style.display = 'none';
        }
        if (e.target === detailModal) {
            detailModal.classList.remove('active');
            detailModal.style.display = 'none';
        }
    });

    // Submit Create Ticket Form
    const createForm = document.getElementById('createTicketForm');
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Show hamster loading overlay
            const hamsterOverlay = document.getElementById('hamsterLoadingOverlay');
            if (hamsterOverlay) {
                hamsterOverlay.style.display = 'flex';
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        hamsterOverlay.classList.add('active');
                    });
                });
            }

            const formData = new FormData();
            formData.append('subject', document.getElementById('createSubject').value);
            formData.append('description', document.getElementById('createDescription').value);
            formData.append('category_id', document.getElementById('createCategory').value);
            formData.append('priority_id', document.getElementById('createPriority').value);
            formData.append('status_id', document.getElementById('createStatus').value);
            formData.append('assigned_to_id', document.getElementById('createAssignee').value);
            formData.append('start_date', document.getElementById('createStartDate') ? document.getElementById('createStartDate').value : '');
            formData.append('due_date', document.getElementById('createDueDate').value);

            // Append all accumulated attachments
            if (window.selectedCreateFiles && window.selectedCreateFiles.length > 0) {
                window.selectedCreateFiles.forEach(file => {
                    formData.append('attachments', file);
                });
            }

            try {
                const res = await fetch('/api/tickets/create/', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                // Hide hamster loading overlay with smooth fade out
                if (hamsterOverlay) {
                    hamsterOverlay.classList.remove('active');
                    setTimeout(() => { hamsterOverlay.style.display = 'none'; }, 300);
                }

                if (data.success) {
                    window.selectedCreateFiles = [];
                    if (window.updateCreateAttachmentsPreview) window.updateCreateAttachmentsPreview();

                    const createAnother = document.getElementById('createAnotherCheck');
                    if (createAnother && createAnother.checked) {
                        document.getElementById('createSubject').value = '';
                        document.getElementById('createDescription').value = '';
                        const startEl = document.getElementById('createStartDate');
                        if (startEl) startEl.value = '';
                        const dueEl = document.getElementById('createDueDate');
                        if (dueEl) dueEl.value = '';
                        alert('Ticket ' + data.ticket_code + ' created successfully!');
                    } else {
                        location.reload();
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (err) {
                // Hide hamster on error too
                if (hamsterOverlay) {
                    hamsterOverlay.classList.remove('active');
                    setTimeout(() => { hamsterOverlay.style.display = 'none'; }, 300);
                }
                console.error(err);
            }
        });
    }

    // Helper: Assign to me in Create Ticket Modal
    window.assignCreateToMe = function() {
        const btn = document.getElementById('btnAssignCreateToMe');
        const select = document.getElementById('createAssignee');
        if (btn && select) {
            const currentUserId = btn.dataset.userId;
            if (currentUserId) {
                select.value = currentUserId;
            }
        }
    };

    // Helper: Description Formatting Toolbar in Create Ticket Modal
    window.insertCreateDescFormat = function(fmt) {
        const textarea = document.getElementById('createDescription');
        if (!textarea) return;
        if (fmt === '/ai ') {
            textarea.value += '\n/ai ';
        } else if (fmt === 'heading') {
            textarea.value += '\n### ';
        } else if (fmt === 'bold') {
            textarea.value += ' **bold text** ';
        } else if (fmt === 'list') {
            textarea.value += '\n- Item 1\n- Item 2';
        } else if (fmt === 'color') {
            textarea.value += ' [color:#579dff]text[/color] ';
        } else if (fmt === 'code') {
            textarea.value += ' ```code block``` ';
        } else if (fmt === 'link') {
            textarea.value += ' [link title](https://example.com) ';
        } else if (fmt === 'emoji') {
            textarea.value += ' 😊 ';
        }
        textarea.focus();
    };


    // Global File Accumulator for Create Ticket Attachments
    window.selectedCreateFiles = [];

    window.updateCreateAttachmentsPreview = function() {
        const previewContainer = document.getElementById('createAttachmentsPreview');
        if (!previewContainer) return;
        previewContainer.innerHTML = '';

        if (!window.selectedCreateFiles || window.selectedCreateFiles.length === 0) return;

        window.selectedCreateFiles.forEach((file, index) => {
            const isImage = file.type.startsWith('image/') || /\.(png|jpe?g|gif|webp|svg)$/i.test(file.name);
            const fileExt = file.name.includes('.') ? file.name.split('.').pop().toUpperCase() : 'FILE';

            const card = document.createElement('div');
            card.style.cssText = 'position:relative; background:#242428; border:1px solid #38383e; border-radius:6px; overflow:hidden; display:flex; flex-direction:column; align-items:center; padding:6px; font-size:11px; text-align:center; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition:all 0.15s ease;';

            const formatSize = (bytes) => {
                if (!bytes) return '0 KB';
                if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
                return Math.round(bytes / 1024) + ' KB';
            };

            // Remove Button Badge
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.innerHTML = '&times;';
            removeBtn.title = 'Remove attachment';
            removeBtn.style.cssText = 'position:absolute; top:4px; right:4px; width:20px; height:20px; border-radius:50%; background:#ff5630; color:#ffffff; border:none; font-size:13px; line-height:1; display:flex; align-items:center; justify-content:center; cursor:pointer; z-index:5; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.4);';
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                window.selectedCreateFiles.splice(index, 1);
                window.updateCreateAttachmentsPreview();
            });

            card.appendChild(removeBtn);

            if (isImage) {
                const imgBox = document.createElement('div');
                imgBox.style.cssText = 'width:100%; height:75px; border-radius:4px; overflow:hidden; background:#121214; margin-bottom:6px; display:flex; align-items:center; justify-content:center;';
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.cssText = 'width:100%; height:100%; object-fit:cover; display:block;';
                imgBox.appendChild(img);
                card.appendChild(imgBox);
            } else {
                const iconBox = document.createElement('div');
                iconBox.style.cssText = 'width:100%; height:75px; border-radius:4px; background:#2c2c32; margin-bottom:6px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#579dff;';
                iconBox.innerHTML = `
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6z"/><polyline points="14 2 14 8 20 8"/></svg>
                    <span style="font-size:9px; font-weight:800; text-transform:uppercase; margin-top:3px; color:#8c9bab;">${fileExt}</span>
                `;
                card.appendChild(iconBox);
            }

            const nameSpan = document.createElement('span');
            nameSpan.style.cssText = 'width:100%; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:#cecfd2; font-weight:600; display:block;';
            nameSpan.textContent = file.name;
            nameSpan.title = file.name;
            card.appendChild(nameSpan);

            const sizeSpan = document.createElement('span');
            sizeSpan.style.cssText = 'font-size:10px; color:#8c9bab; display:block; margin-top:2px;';
            sizeSpan.textContent = formatSize(file.size);
            card.appendChild(sizeSpan);

            previewContainer.appendChild(card);
        });
    };

    // File Input Listener
    const createFileInput = document.getElementById('createAttachments');
    if (createFileInput) {
        createFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                Array.from(e.target.files).forEach(f => {
                    if (!window.selectedCreateFiles.some(existing => existing.name === f.name && existing.size === f.size)) {
                        window.selectedCreateFiles.push(f);
                    }
                });
                window.updateCreateAttachmentsPreview();
                createFileInput.value = '';
            }
        });
    }

    // Drag & Drop Listener for Dropzone Box
    const dropzoneBox = document.querySelector('.attachment-dropzone-box');
    if (dropzoneBox) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzoneBox.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzoneBox.addEventListener(eventName, () => {
                dropzoneBox.style.borderColor = '#579dff';
                dropzoneBox.style.background = '#28282e';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzoneBox.addEventListener(eventName, () => {
                dropzoneBox.style.borderColor = 'var(--jira-border, #38383e)';
                dropzoneBox.style.background = 'var(--jira-card-bg, #1e1e22)';
            }, false);
        });

        dropzoneBox.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length > 0) {
                Array.from(dt.files).forEach(f => {
                    if (!window.selectedCreateFiles.some(existing => existing.name === f.name && existing.size === f.size)) {
                        window.selectedCreateFiles.push(f);
                    }
                });
                window.updateCreateAttachmentsPreview();
            }
        });
    }


    // Inline Create Category Button Handler
    const btnAddCat = document.getElementById('btnInlineAddCategory');
    if (btnAddCat) {
        btnAddCat.addEventListener('click', async () => {
            const catName = prompt("Enter new category name:");
            if (!catName || !catName.trim()) return;
            try {
                const res = await fetch('/api/categories/create/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category_name: catName.trim() })
                });
                const data = await res.json();
                if (data.success) {
                    const selectEl = document.getElementById('createCategory');
                    if (selectEl) {
                        const opt = document.createElement('option');
                        opt.value = data.category_id;
                        opt.textContent = data.category_name;
                        opt.selected = true;
                        selectEl.appendChild(opt);
                    }
                } else {
                    alert(data.error || 'Failed to create category.');
                }
            } catch (err) {
                console.error(err);
                alert('Error creating category.');
            }
        });
    }

    // Add Status Column Button Handler
    const btnAddStatus = document.getElementById('btnAddStatusColumn');
    if (btnAddStatus) {
        btnAddStatus.addEventListener('click', async () => {
            const statusName = prompt("Enter status name:");
            if (!statusName || !statusName.trim()) return;
            try {
                const res = await fetch('/api/statuses/create/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status_name: statusName.trim() })
                });
                const data = await res.json();
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.error || 'Failed to create status.');
                }
            } catch (err) {
                console.error(err);
                alert('Error creating status.');
            }
        });
    }

    // Column Options Context Menu Handlers
    window._currentColumnStatusId = null;
    window._currentColumnStatusName = '';

    window.openColumnContextMenu = function(e, btn, statusId, statusName) {
        e.stopPropagation();
        window._currentColumnStatusId = statusId;
        window._currentColumnStatusName = statusName;

        const menu = document.getElementById('columnContextMenu');
        if (!menu) return;

        const rect = btn.getBoundingClientRect();
        menu.style.display = 'block';
        menu.style.top = (rect.bottom + 4) + 'px';
        menu.style.left = (rect.right - 180) + 'px';
    };

    window.moveColumnAction = async function(direction) {
        const statusId = window._currentColumnStatusId;
        if (!statusId) return;
        try {
            const res = await fetch(`/api/statuses/${statusId}/move/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ direction: direction })
            });
            const data = await res.json();
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'Failed to move column.');
            }
        } catch (err) {
            console.error(err);
        }
    };

    window.deleteColumnAction = async function() {
        const statusId = window._currentColumnStatusId;
        const statusName = window._currentColumnStatusName || 'this status';
        if (!statusId) return;

        if (!confirm(`Are you sure you want to delete status "${statusName}"?`)) return;

        try {
            const res = await fetch(`/api/statuses/${statusId}/delete/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'Failed to delete status.');
            }
        } catch (err) {
            console.error(err);
            alert('Error deleting status.');
        }
    };

    document.addEventListener('click', (e) => {
        const menu = document.getElementById('columnContextMenu');
        if (menu && !e.target.closest('#columnContextMenu') && !e.target.closest('.col-menu-btn')) {
            menu.style.display = 'none';
        }
    });

    // ---------------- LEFT SIDEBAR RESIZER CONTROLLER ----------------
    (function initSidebarResizer() {
        const sidebar = document.getElementById('jiraSidebar');
        const resizer = document.getElementById('sidebarResizer');
        if (!sidebar || !resizer) return;

        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        // Restore saved sidebar width if present in localStorage
        const savedWidth = localStorage.getItem('jira_sidebar_width');
        if (savedWidth) {
            sidebar.style.width = savedWidth + 'px';
        }

        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startWidth = sidebar.getBoundingClientRect().width;
            resizer.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            const dx = e.clientX - startX;
            let newWidth = startWidth + dx;

            // Enforce minimum and maximum bounds (160px - 480px)
            if (newWidth < 160) newWidth = 160;
            if (newWidth > 480) newWidth = 480;

            sidebar.style.width = newWidth + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                resizer.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';

                // Save preferred width to localStorage
                const currentWidth = sidebar.getBoundingClientRect().width;
                localStorage.setItem('jira_sidebar_width', currentWidth);
            }
        });
    })();

    // ---------------- REAL-TIME LIVE KANBAN BOARD SYNC (HIGH PERFORMANCE) ----------------
    (function initRealtimeBoardSync() {

        let currentBoardVersion = 0;

        async function checkBoardSync() {
            // Only poll if tab is visible AND user is on the Kanban board page
            if (document.hidden) return;
            const boardContainer = document.querySelector('.kanban-board-container');
            if (!boardContainer) return;

            try {
                const res = await fetch(`/api/board/sync/?ver=${currentBoardVersion}`);
                const data = await res.json();

                if (!data) return;

                // Initial version setup
                if (currentBoardVersion === 0) {
                    currentBoardVersion = data.ver;
                    return;
                }

                // If another user moved a ticket or updated board
                if (data.updated && data.ver !== currentBoardVersion) {
                    currentBoardVersion = data.ver;
                    applyLiveBoardUpdates(data.tickets, data.column_counts);
                }
            } catch (err) {
                // Quietly handle intermittent network issues
            }
        }

        function createCardElement(t) {
            const card = document.createElement('div');
            card.className = 'ticket-card';
            card.setAttribute('draggable', 'true');
            card.setAttribute('data-ticket-id', t.ticket_id);

            let prioIcon = '';
            if (t.priority_name === 'Highest') {
                prioIcon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5630" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:block;"><polyline points="17 11 12 6 7 11"></polyline><polyline points="17 17 12 12 7 17"></polyline></svg>`;
            } else if (t.priority_name === 'High') {
                prioIcon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5630" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:block;"><polyline points="18 15 12 9 6 15"></polyline></svg>`;
            } else if (t.priority_name === 'Medium') {
                prioIcon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff9900" stroke-width="2.5" stroke-linecap="round" style="display:block;"><line x1="5" y1="9" x2="19" y2="9"></line><line x1="5" y1="15" x2="19" y2="15"></line></svg>`;
            } else if (t.priority_name === 'Low') {
                prioIcon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0065ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:block;"><polyline points="6 9 12 15 18 9"></polyline></svg>`;
            } else {
                prioIcon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0065ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:block;"><polyline points="6 11 12 17 18 11"></polyline><polyline points="6 5 12 11 18 5"></polyline></svg>`;
            }

            const isDone = ['done', 'resolved', 'closed'].includes(String(t.status_name).toLowerCase());
            const keyIcon = isDone 
                ? `<div class="key-icon-box key-icon-green" title="Done"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>`
                : `<div class="key-icon-box key-icon-blue" title="Task"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg></div>`;

            let avatarHtml = '';
            if (t.assignee_image) {
                avatarHtml = `<div class="assignee-avatar-icon" title="${t.assignee}"><img src="${t.assignee_image}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;"></div>`;
            } else if (t.assignee_initials) {
                avatarHtml = `<div class="assignee-avatar-icon" style="background:${t.assignee_color || '#0052cc'}; color:#ffffff;" title="${t.assignee}">${t.assignee_initials}</div>`;
            } else {
                avatarHtml = `<div class="assignee-avatar-icon unassigned-avatar" title="Unassigned"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>`;
            }

            let dueDateHtml = '';
            if (t.due_date_formatted) {
                const dueColor = t.is_due_soon ? 'color:#ff5630; font-weight:600;' : '';
                const dueIcon = t.is_due_soon ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5630" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" title="Due within 1 day or overdue" style="flex-shrink:0;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>` : '';
                dueDateHtml = `<div><div class="card-due-label">Due date</div><div class="card-due-date" style="display:inline-flex; align-items:center; gap:4px; ${dueColor}"><span>${t.due_date_formatted}</span>${dueIcon}</div></div>`;
            }

            card.innerHTML = `
                <div class="card-title">
                    <span>${t.subject}</span>
                    <button type="button" class="card-menu-btn no-modal" onclick="openCardMenu(event, this, ${t.ticket_id}, '${t.ticket_code}', ${t.status_id})" title="Actions">•••</button>
                </div>
                ${dueDateHtml}
                <div class="card-key-row">
                    <div class="key-tag">
                        ${keyIcon}
                        <span>${t.ticket_code}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <button type="button" class="card-priority-btn no-modal" data-ticket-id="${t.ticket_id}" data-priority-id="${t.priority_id}" data-priority-name="${t.priority_name}" onclick="openPriorityMenu(event, this)" title="Change Priority" style="width:22px; height:22px; padding:0; align-self:center;">
                            ${prioIcon}
                        </button>
                        ${avatarHtml}
                    </div>
                </div>
            `;

            return card;
        }

        function applyLiveBoardUpdates(tickets, columnCounts) {
            if (!tickets) return;

            const validTicketIds = new Set(tickets.map(t => String(t.ticket_id)));

            // 1. Remove deleted tickets from DOM if no longer in ticket list
            document.querySelectorAll('.ticket-card[data-ticket-id]').forEach(card => {
                const tid = card.getAttribute('data-ticket-id');
                if (tid && !validTicketIds.has(String(tid))) {
                    card.style.transition = 'all 0.3s ease';
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.8)';
                    setTimeout(() => { card.remove(); }, 300);
                }
            });

            // 2. Update column positions or render newly created tickets
            tickets.forEach(t => {
                let card = document.querySelector(`.ticket-card[data-ticket-id="${t.ticket_id}"]`);
                if (t.status_id) {
                    const targetColumnContainer = document.querySelector(`.column-cards-container[data-status-id="${t.status_id}"]`);
                    if (targetColumnContainer) {
                        if (!card) {
                            // NEW TICKET CREATED ON ANOTHER DEVICE! Build and append new card to column
                            card = createCardElement(t);
                            targetColumnContainer.appendChild(card);
                            card.style.animation = 'fadeInCard 0.25s ease-out';
                            if (window.updateCardStatusIcon) window.updateCardStatusIcon(card);
                        } else if (card.parentElement !== targetColumnContainer) {
                            // TICKET MOVED TO DIFFERENT COLUMN!
                            card.style.transition = 'transform 0.25s ease, opacity 0.25s ease';
                            card.style.opacity = '0.3';
                            card.style.transform = 'scale(0.95)';

                            setTimeout(() => {
                                targetColumnContainer.appendChild(card);
                                card.style.opacity = '1';
                                card.style.transform = 'scale(1)';
                                setTimeout(() => { card.style.transition = ''; }, 300);
                            }, 180);
                        }
                    }
                }
            });

            // 3. Update column card counts
            if (columnCounts) {
                Object.keys(columnCounts).forEach(statusId => {
                    const colContainer = document.querySelector(`.column-cards-container[data-status-id="${statusId}"]`);
                    if (colContainer) {
                        const col = colContainer.closest('.kanban-column');
                        if (col) {
                            const countBadge = col.querySelector('.column-count');
                            if (countBadge) countBadge.textContent = columnCounts[statusId];
                        }
                    }
                });
            }
        }


        // Smart polling interval (3 seconds)
        setInterval(checkBoardSync, 3000);

        // Immediately check when switching back to tab
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                checkBoardSync();
            }
        });

        // Initialize Global Board Pusher Channel for real-time live deletes, creates, and status updates across devices
        if (typeof Pusher !== 'undefined' && !window._globalBoardPusherBound) {
            window._globalBoardPusherBound = true;
            try {
                if (!window._pusherClient) {
                    window._pusherClient = new Pusher('308cbea8f43adedfd722', { cluster: 'ap1' });
                }
                const boardChannel = window._pusherClient.subscribe('board_channel');

                boardChannel.bind('ticket-deleted', function(data) {
                    if (!data || !data.ticket_id) return;
                    const targetId = String(data.ticket_id);
                    document.querySelectorAll('.ticket-card').forEach(card => {
                        const cardId = String(card.getAttribute('data-ticket-id') || card.dataset.ticketId);
                        if (cardId === targetId) {
                            card.style.transition = 'all 0.3s ease';
                            card.style.opacity = '0';
                            card.style.transform = 'scale(0.8)';
                            setTimeout(() => {
                                card.remove();
                                if (window.updateColumnCounts) window.updateColumnCounts();
                            }, 300);
                        }
                    });
                    if (window._currentTicketData && String(window._currentTicketData.ticket_id) === targetId) {
                        const modal = document.getElementById('ticketDetailModal');
                        if (modal) {
                            modal.classList.remove('active');
                            modal.style.display = 'none';
                        }
                    }
                });

                boardChannel.bind('ticket-created', function(data) {
                    if (data && data.ticket_id && data.status_id) {
                        let card = document.querySelector(`.ticket-card[data-ticket-id="${data.ticket_id}"]`);
                        if (!card) {
                            const targetColumnContainer = document.querySelector(`.column-cards-container[data-status-id="${data.status_id}"]`);
                            if (targetColumnContainer) {
                                card = createCardElement(data);
                                targetColumnContainer.appendChild(card);
                                card.style.animation = 'fadeInCard 0.25s ease-out';
                                if (window.updateCardStatusIcon) window.updateCardStatusIcon(card);
                                if (window.updateColumnCounts) window.updateColumnCounts();
                            }
                        }
                    }
                    checkBoardSync();
                });

                boardChannel.bind('ticket-updated', function() {
                    checkBoardSync();
                });
            } catch (err) {
                console.warn('Pusher board sync error:', err);
            }
        }

    })();






    // Attachment Filter Buttons Handler
    document.querySelectorAll('.att-filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.att-filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            window.currentAttFilter = btn.dataset.filter;
            if (window.renderAttachments) window.renderAttachments();
        });
    });

    // Attachment Modal Direct Upload Handler
    const modalUploadInput = document.getElementById('modalUploadInput');
    if (modalUploadInput) {
        modalUploadInput.addEventListener('change', async () => {
            const addCommBtn = document.getElementById('addCommentBtn');
            const ticketId = addCommBtn ? addCommBtn.dataset.ticketId : null;
            if (!ticketId || modalUploadInput.files.length === 0) return;

            const formData = new FormData();
            for (let i = 0; i < modalUploadInput.files.length; i++) {
                formData.append('attachments', modalUploadInput.files[i]);
            }

            try {
                const res = await fetch(`/api/tickets/${ticketId}/upload-attachment/`, {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.success) {
                    modalUploadInput.value = '';
                    window.openTicketDetailModal(ticketId);
                } else {
                    alert('Upload failed: ' + data.error);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    // Attachment Dropzone Drag & Drop Handler
    const dropzone = document.querySelector('.attachment-dropzone-box');
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('drag-over');
            }, false);
        });

        dropzone.addEventListener('drop', async (e) => {
            const files = e.dataTransfer.files;
            const addCommBtn = document.getElementById('addCommentBtn');
            const ticketId = addCommBtn ? addCommBtn.dataset.ticketId : null;
            if (!ticketId || !files || files.length === 0) return;

            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('attachments', files[i]);
            }

            try {
                const res = await fetch(`/api/tickets/${ticketId}/upload-attachment/`, {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.success) {
                    window.openTicketDetailModal(ticketId);
                } else {
                    alert('Upload failed: ' + data.error);
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    // Quick Reply Helper for Comments
    window.appendQuickReply = function(text) {
        const input = document.getElementById('newCommentInput');
        if (input) {
            if (input.value) {
                input.value += ' ' + text;
            } else {
                input.value = text;
            }
            input.focus();
        }
    };

    // Activity Tabs Handler (Comments / History / All)
    document.querySelectorAll('.activity-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.activity-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const tab = btn.dataset.tab;
            const commentsView = document.getElementById('activityCommentsView');
            const historyView = document.getElementById('activityHistoryView');
            
            if (tab === 'history') {
                if (historyView) historyView.style.display = 'block';
                if (commentsView) commentsView.style.display = 'none';
            } else if (tab === 'all') {
                if (historyView) historyView.style.display = 'block';
                if (commentsView) commentsView.style.display = 'block';
            } else {
                if (commentsView) commentsView.style.display = 'block';
                if (historyView) historyView.style.display = 'none';
            }
        });
    });

    // Add Comment Handler
    const addCommentBtn = document.getElementById('addCommentBtn');
    if (addCommentBtn) {
        addCommentBtn.addEventListener('click', async () => {
            const ticketId = addCommentBtn.dataset.ticketId;
            const input = document.getElementById('newCommentInput');
            const text = input ? input.value.trim() : '';
            if (!text || !ticketId) return;

            try {
                const res = await fetch(`/api/tickets/${ticketId}/comments/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ comment_text: text })
                });
                const data = await res.json();
                if (data.success) {
                    if (input) input.value = '';
                    window.openTicketDetailModal(ticketId); // Refresh modal
                }
            } catch (err) {
                console.error(err);
            }
        });
    }
});

// Jira Comment Editor Format Helpers
window.insertCommentFormat = function(type) {
    const input = document.getElementById('newCommentInput');
    if (!input) return;

    input.focus();
    const start = input.selectionStart || 0;
    const end = input.selectionEnd || 0;
    const selected = input.value.substring(start, end);

    let replacement = '';
    if (type === 'bold') {
        replacement = selected ? `**${selected}**` : '**bold text**';
    } else if (type === 'heading') {
        replacement = selected ? `### ${selected}` : '### Heading\n';
    } else if (type === 'list') {
        replacement = selected ? selected.split('\n').map(l => `- ${l}`).join('\n') : '- list item\n';
    } else if (type === 'code') {
        replacement = selected ? `\`\`\`\n${selected}\n\`\`\`` : '```\ncode block\n```';
    } else if (type === 'emoji') {
        replacement = '😊 ';
    } else if (type === 'link') {
        replacement = selected ? `[${selected}](https://)` : '[link text](https://)';
    } else if (type === '/ai ') {
        replacement = '/ai ';
    } else if (type === 'plus') {
        replacement = '\n---\n';
    } else if (type === 'color') {
        replacement = selected ? `<span style="color:#579dff">${selected}</span>` : '<span style="color:#579dff">colored text</span>';
    } else if (type === 'undo' || type === 'redo' || type === 'history') {
        return;
    } else {
        replacement = type;
    }

    input.value = input.value.substring(0, start) + replacement + input.value.substring(end);
    input.dispatchEvent(new Event('input'));
};

window.clearCommentInput = function() {
    const input = document.getElementById('newCommentInput');
    if (input) input.value = '';
};

// Comment Image Upload & Formatting Helpers
window.formatCommentText = function(text) {
    if (!text) return '';

    // Escape HTML first to prevent XSS except for our controlled tags
    let safeText = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

    // Markdown image syntax: ![alt](url)
    safeText = safeText.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
        const cleanUrl = url.replace(/&amp;/g, '&');
        return `<div style="margin-top:8px; margin-bottom:8px;"><img src="${cleanUrl}" alt="${alt}" style="max-width:100%; max-height:450px; border-radius:8px; border:1px solid rgba(255,255,255,0.12); cursor:pointer; display:block;" onclick="window.open('${cleanUrl}', '_blank')" title="Click to view full image"></div>`;
    });

    // Bold formatting: **text**
    safeText = safeText.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Convert newlines to <br> if not inside HTML tags
    if (!safeText.includes('<img')) {
        safeText = safeText.replace(/\n/g, '<br>');
    } else {
        safeText = safeText.replace(/\n(?![^<]*>)/g, '<br>');
    }

    return safeText;
};

window.triggerCommentFileUpload = function() {
    const commentImageInput = document.getElementById('commentImageInput');
    if (commentImageInput) {
        commentImageInput.click();
    } else {
        const modalUploadInput = document.getElementById('modalUploadInput');
        if (modalUploadInput) modalUploadInput.click();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Comment Image File Input Listener (Uploads for inline comment display, NOT ticket Attachments)
    const commentImageInput = document.getElementById('commentImageInput');
    if (commentImageInput) {
        commentImageInput.addEventListener('change', async () => {
            if (commentImageInput.files.length === 0) return;

            const formData = new FormData();
            for (let i = 0; i < commentImageInput.files.length; i++) {
                formData.append('image', commentImageInput.files[i]);
            }

            try {
                const res = await fetch('/api/comments/upload-image/', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.success && data.url) {
                    const input = document.getElementById('newCommentInput');
                    if (input) {
                        const imgTag = `\n![image](${data.url})\n`;
                        input.value += imgTag;
                        input.focus();
                    }
                    commentImageInput.value = '';
                } else {
                    alert('Image upload failed: ' + (data.error || 'Unknown error'));
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    // Comment Textarea Paste Image Listener (Paste directly from clipboard Ctrl+V)
    const commentInput = document.getElementById('newCommentInput');
    if (commentInput) {
        commentInput.addEventListener('paste', async (e) => {
            const items = (e.clipboardData || e.originalEvent.clipboardData)?.items;
            if (!items) return;
            let imageFile = null;
            for (let item of items) {
                if (item.type.indexOf('image') === 0) {
                    imageFile = item.getAsFile();
                    break;
                }
            }
            if (imageFile) {
                e.preventDefault();
                const formData = new FormData();
                formData.append('image', imageFile);

                try {
                    const res = await fetch('/api/comments/upload-image/', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (data.success && data.url) {
                        const imgTag = `\n![image](${data.url})\n`;
                        const start = commentInput.selectionStart || 0;
                        const end = commentInput.selectionEnd || 0;
                        commentInput.value = commentInput.value.substring(0, start) + imgTag + commentInput.value.substring(end);
                    }
                } catch (err) {
                    console.error(err);
                }
            }
        });
    }
});

// =====================================================================
// SHARED FLOATING CARD CONTEXT MENU
// =====================================================================

// Collect all statuses from the DOM columns at page load
window._cardMenuCurrentTicketId = null;
window._cardMenuCurrentTicketCode = null;
window._cardMenuIsModal = false;

// Gather status list from column containers (they have data-status-id)
function getStatusList() {
    const statuses = [];
    document.querySelectorAll('.column-cards-container[data-status-id]').forEach(col => {
        const id = col.dataset.statusId;
        // Find the header in the parent kanban-column
        const header = col.closest('.kanban-column');
        const name = header ? header.querySelector('.column-header span:first-child')?.textContent?.trim() : null;
        if (id && name) statuses.push({ id, name });
    });
    if (statuses.length === 0) {
        return [
            { id: '1', name: 'To Do' },
            { id: '2', name: 'In Progress' },
            { id: '3', name: 'In Review' },
            { id: '4', name: 'Done' }
        ];
    }
    return statuses;
}

function buildCardMenuStatuses(currentStatusId, isModal) {
    const container = document.getElementById('cardMenuStatuses');
    if (!container) return;
    container.innerHTML = '';

    // Color map for status dots
    const dotColors = {
        'to-do': '#42526e', 'open': '#42526e',
        'in-progress': '#0052cc',
        'in-review': '#6554c0',
        'done': '#36b37e', 'closed': '#36b37e'
    };

    getStatusList().forEach(st => {
        const slugName = st.name.toLowerCase().replace(/\s+/g, '-');
        const dotColor = dotColors[slugName] || '#626f86';
        const isActive = String(st.id) === String(currentStatusId);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.style.cssText = `
            display:flex; align-items:center; gap:10px;
            width:100%; padding:7px 14px; background:${isActive ? 'rgba(87,157,255,0.12)' : 'transparent'};
            border:none; color:${isActive ? '#579dff' : '#cecfd2'}; font-size:13px;
            font-weight:${isActive ? '700' : '400'};
            cursor:pointer; text-align:left;
        `;
        btn.onmouseover = () => { if (!isActive) btn.style.background = 'rgba(255,255,255,0.06)'; };
        btn.onmouseout = () => { if (!isActive) btn.style.background = 'transparent'; };

        btn.innerHTML = `
            <span style="width:8px;height:8px;border-radius:50%;background:${dotColor};display:inline-block;flex-shrink:0;"></span>
            <span>${st.name}</span>
        `;
        btn.onclick = () => {
            closeCardMenu();
            if (isModal) {
                changeModalTicketStatus(st.id);
            } else {
                changeTicketStatusFromCard(null, window._cardMenuCurrentTicketId, st.id);
            }
        };
        container.appendChild(btn);
    });
}

function openCardMenu(e, btn, ticketId, ticketCode, currentStatusId) {
    if (e) { e.stopPropagation(); e.preventDefault(); }

    window._cardMenuCurrentTicketId = ticketId;
    window._cardMenuCurrentTicketCode = ticketCode;
    window._cardMenuIsModal = false;

    const menu = document.getElementById('cardContextMenu');
    if (!menu) return;

    // Dynamically retrieve actual status ID from the card's column container if available
    if (btn) {
        const cardCol = btn.closest('.column-cards-container');
        if (cardCol && cardCol.dataset && cardCol.dataset.statusId) {
            currentStatusId = cardCol.dataset.statusId;
        }
    }

    // Check if already open for this same button → toggle close
    if (menu.style.display === 'block' && menu._openBtn === btn) {
        closeCardMenu();
        return;
    }

    buildCardMenuStatuses(currentStatusId, false);
    menu._openBtn = btn;

    // Position first (hidden), then measure and show
    menu.style.visibility = 'hidden';
    menu.style.display = 'block';

    const rect = btn.getBoundingClientRect();
    let top = rect.bottom + 4;
    let left = rect.right - menu.offsetWidth;
    if (left < 8) left = 8;
    if (left + menu.offsetWidth > window.innerWidth - 8) left = window.innerWidth - menu.offsetWidth - 8;
    if (top + menu.offsetHeight > window.innerHeight - 8) top = rect.top - menu.offsetHeight - 4;

    menu.style.top = top + 'px';
    menu.style.left = left + 'px';
    menu.style.visibility = 'visible';
}

function openModalMenu(e, btn) {
    if (e) { e.stopPropagation(); e.preventDefault(); }

    const ticketId = window._currentTicketId || (window._currentTicketData ? window._currentTicketData.ticket_id : null);
    if (!ticketId) return;

    window._cardMenuCurrentTicketId = ticketId;
    window._cardMenuCurrentTicketCode = document.getElementById('detailCode')?.textContent || '';
    window._cardMenuIsModal = true;


    const statusSelect = document.getElementById('detailStatusSelect');
    const currentStatusId = statusSelect ? statusSelect.value : null;

    const menu = document.getElementById('cardContextMenu');
    if (!menu) return;

    if (menu.style.display === 'block' && menu._openBtn === btn) {
        closeCardMenu();
        return;
    }

    buildCardMenuStatuses(currentStatusId, true);
    menu._openBtn = btn;

    menu.style.visibility = 'hidden';
    menu.style.display = 'block';

    const rect = btn.getBoundingClientRect();
    let top = rect.bottom + 4;
    let left = rect.right - menu.offsetWidth;
    if (left < 8) left = 8;
    if (left + menu.offsetWidth > window.innerWidth - 8) left = window.innerWidth - menu.offsetWidth - 8;
    if (top + menu.offsetHeight > window.innerHeight - 8) top = rect.top - menu.offsetHeight - 4;

    menu.style.top = top + 'px';
    menu.style.left = left + 'px';
    menu.style.visibility = 'visible';
}

function closeCardMenu() {
    const menu = document.getElementById('cardContextMenu');
    if (menu) menu.style.display = 'none';
}

// Close menu on outside click
document.addEventListener('click', (e) => {
    const menu = document.getElementById('cardContextMenu');
    if (!menu || menu.style.display === 'none' || menu.style.visibility === 'hidden') return;
    // Don't close if clicking inside the menu itself or clicking any card-menu-btn
    if (menu.contains(e.target)) return;
    if (e.target.closest('.card-menu-btn') || e.target.closest('[onclick*="openCardMenu"]') || e.target.closest('[onclick*="openModalMenu"]')) return;
    closeCardMenu();
});

// Edit ticket from context menu
window.cardMenuEditTicket = function() {
    closeCardMenu();
    if (window._currentTicketCanEdit === false) {
        alert('Permission Denied: Your role only has View access and cannot edit tickets.');
        return;
    }
    const ticketId = window._cardMenuCurrentTicketId;
    if (ticketId) {
        openEditTicketModal(ticketId);
    }
};

window.openEditTicketModal = function(ticketId) {
    const editModal = document.getElementById('editTicketModal');
    if (!editModal) return;

    const alertEl = document.getElementById('editTicketAlert');
    if (alertEl) alertEl.style.display = 'none';

    const t = window._currentTicketData || {};
    document.getElementById('editTicketCodeBadge').textContent = t.ticket_code ? `[${t.ticket_code}]` : '';
    document.getElementById('editSubject').value = t.subject || '';
    document.getElementById('editDescription').value = t.description || '';
    if (document.getElementById('editAssignee')) document.getElementById('editAssignee').value = t.assignee_id || '';
    if (document.getElementById('editPriority')) document.getElementById('editPriority').value = t.priority_id || 3;
    if (document.getElementById('editCategory')) document.getElementById('editCategory').value = t.category_id || 1;
    if (document.getElementById('editStartDate')) document.getElementById('editStartDate').value = t.start_date || '';
    if (document.getElementById('editDueDate')) document.getElementById('editDueDate').value = t.due_date || '';

    editModal.dataset.ticketId = ticketId;
    editModal.style.display = 'flex';
};

window.assignEditToMe = function() {
    const btn = document.getElementById('btnAssignEditToMe');
    const select = document.getElementById('editAssignee');
    if (btn && select) {
        const currentUserId = btn.dataset.userId;
        if (currentUserId) {
            select.value = currentUserId;
        }
    }
};

window.insertEditDescFormat = function(fmt) {
    const textarea = document.getElementById('editDescription');
    if (!textarea) return;
    if (fmt === '/ai ') {
        textarea.value += '\n/ai ';
    } else if (fmt === 'heading') {
        textarea.value += '\n### ';
    } else if (fmt === 'bold') {
        textarea.value += ' **bold text** ';
    } else if (fmt === 'list') {
        textarea.value += '\n- Item 1\n- Item 2';
    } else if (fmt === 'color') {
        textarea.value += ' [color:#579dff]text[/color] ';
    } else if (fmt === 'code') {
        textarea.value += ' ```code block``` ';
    } else if (fmt === 'link') {
        textarea.value += ' [link title](https://example.com) ';
    } else if (fmt === 'emoji') {
        textarea.value += ' 😊 ';
    }
    textarea.focus();
};

window.closeEditTicketModal = function() {
    const editModal = document.getElementById('editTicketModal');
    if (editModal) editModal.style.display = 'none';
};


window.copyInviteLink = function() {
    const inviteUrl = window.location.origin + '/board/';
    navigator.clipboard.writeText(inviteUrl).then(() => {
        alert('Invite link copied to clipboard: ' + inviteUrl);
    }).catch(err => {
        console.error('Could not copy link', err);
    });
};

window.updateRoleDescription = function() {
    const roleSelect = document.getElementById('addRoleSelect');
    const descBox = document.getElementById('roleDescriptionBox');
    if (!roleSelect || !descBox) return;

    const descriptions = {
        'Administrator': 'Admins can do most things, like update settings and add other admins.',
        'Member': 'Members are part of the team, and can add, edit, and collaborate on all work.',
        'Support Agent': 'Support agents can view, update, assign, and resolve tickets.',
        'Viewer': 'Viewers can search through, view, and comment on your team\'s work, but not much else.'
    };

    const val = roleSelect.value;
    descBox.textContent = descriptions[val] || descriptions['Member'];
};

// Delete from context menu
window.cardMenuDeleteTicket = async function() {
    const ticketId = window._cardMenuCurrentTicketId;
    const ticketCode = window._cardMenuCurrentTicketCode;
    const isModal = window._cardMenuIsModal;
    if (!ticketId) return;

    closeCardMenu();
    if (!confirm(`Are you sure you want to delete ticket ${ticketCode || ''}?`)) return;

    try {
        const res = await fetch(`/api/tickets/${ticketId}/delete/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (data.success) {
            if (isModal) {
                const detailModal = document.getElementById('ticketDetailModal');
                if (detailModal) {
                    detailModal.classList.remove('active');
                    detailModal.style.display = 'none';
                }
            }
            const card = document.querySelector(`.ticket-card[data-ticket-id="${ticketId}"]`);
            if (card) {
                card.style.transition = 'all 0.2s ease';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    card.remove();
                    if (window.updateColumnCounts) window.updateColumnCounts();
                }, 200);
            } else {
                location.reload();
            }
        } else {
            alert('Failed to delete ticket: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error(err);
    }
};

// Status change from card (keep existing function working)
window.changeTicketStatusFromCard = async function(e, ticketId, statusId) {
    if (e) e.stopPropagation();
    try {
        const res = await fetch(`/api/tickets/${ticketId}/update-status/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status_id: statusId })
        });
        const data = await res.json();
        if (data.success) {
            const card = document.querySelector(`.ticket-card[data-ticket-id="${ticketId}"]`);
            const targetColumn = document.querySelector(`.column-cards-container[data-status-id="${statusId}"]`);
            if (card && targetColumn) {
                targetColumn.appendChild(card);
                if (window.updateCardStatusIcon) window.updateCardStatusIcon(card, statusId);
                if (window.updateColumnCounts) window.updateColumnCounts();
            } else {
                location.reload();
            }
            const statusSelect = document.getElementById('detailStatusSelect');
            if (statusSelect && window._currentTicketData && String(window._currentTicketData.ticket_id) === String(ticketId)) {
                statusSelect.value = statusId;
            }
        } else {
            alert('Failed to update status: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error(err);
    }
};

// Status change from modal
window.changeModalTicketStatus = async function(statusId) {
    const addCommBtn = document.getElementById('addCommentBtn');
    const ticketId = addCommBtn ? addCommBtn.dataset.ticketId : null;
    if (!ticketId) return;

    try {
        const res = await fetch(`/api/tickets/${ticketId}/update-status/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status_id: statusId })
        });
        const data = await res.json();
        if (data.success) {
            const statusSelect = document.getElementById('detailStatusSelect');
            if (statusSelect) statusSelect.value = statusId;
            const card = document.querySelector(`.ticket-card[data-ticket-id="${ticketId}"]`);
            const targetColumn = document.querySelector(`.column-cards-container[data-status-id="${statusId}"]`);
            if (card && targetColumn) {
                targetColumn.appendChild(card);
                if (window.updateCardStatusIcon) window.updateCardStatusIcon(card, statusId);
                if (window.updateColumnCounts) window.updateColumnCounts();
            }
        } else {
            alert('Failed to update status: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error(err);
    }
};

// Expose for modal open button click
window.openCardMenu = openCardMenu;
window.openModalMenu = openModalMenu;

// =====================================================================
// PRIORITY PICKER POPUP
// =====================================================================

const PRIORITY_CONFIGS = [
    {
        id: null, name: 'Highest',
        color: '#ff5630',
        icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5630" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 11 12 6 7 11"></polyline><polyline points="17 17 12 12 7 17"></polyline></svg>`
    },
    {
        id: null, name: 'High',
        color: '#ff5630',
        icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff5630" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>`
    },
    {
        id: null, name: 'Medium',
        color: '#ff9900',
        icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff9900" stroke-width="2.5" stroke-linecap="round"><line x1="5" y1="9" x2="19" y2="9"></line><line x1="5" y1="15" x2="19" y2="15"></line></svg>`
    },
    {
        id: null, name: 'Low',
        color: '#2684ff',
        icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2684ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>`
    },
    {
        id: null, name: 'Lowest',
        color: '#2684ff',
        icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2684ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="7 7 12 12 17 7"></polyline><polyline points="7 13 12 18 17 13"></polyline></svg>`
    }
];

// Load priority IDs dynamically from the list-view prio dropdowns if present,
// otherwise we rely on the server returning priority_id in the API response.
function getPriorityIcon(name) {
    const p = PRIORITY_CONFIGS.find(c => c.name === name);
    return p ? p.icon : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#626f86" stroke-width="2" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>`;
}

window._priorityCurrentBtn = null;
window._priorityCurrentTicketId = null;

function buildPriorityList(currentPriorityName) {
    const container = document.getElementById('priorityPickerList');
    if (!container) return;
    container.innerHTML = '';

    PRIORITY_CONFIGS.forEach(p => {
        const isActive = p.name === currentPriorityName;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.style.cssText = `
            display:flex; align-items:center; gap:10px;
            width:100%; padding:8px 14px;
            background:${isActive ? 'rgba(87,157,255,0.12)' : 'transparent'};
            border:none; color:${isActive ? '#579dff' : '#cecfd2'};
            font-size:13px; font-weight:${isActive ? '700' : '400'};
            cursor:pointer; text-align:left;
        `;
        btn.onmouseover = () => { if (!isActive) btn.style.background = 'rgba(255,255,255,0.06)'; };
        btn.onmouseout = () => { if (!isActive) btn.style.background = 'transparent'; };
        btn.innerHTML = `${p.icon} <span>${p.name}</span>`;
        btn.onclick = () => {
            closePriorityMenu();
            changePriority(window._priorityCurrentTicketId, p.name);
        };
        container.appendChild(btn);
    });
}

function openPriorityMenu(e, btn) {
    if (e) { e.stopPropagation(); e.preventDefault(); }

    const menu = document.getElementById('priorityPickerMenu');
    if (!menu) return;

    // Toggle off if same button
    if (menu.style.display === 'block' && window._priorityCurrentBtn === btn) {
        closePriorityMenu();
        return;
    }

    window._priorityCurrentBtn = btn;
    window._priorityCurrentTicketId = btn.dataset.ticketId;
    const currentPriorityName = btn.dataset.priorityName || '';

    buildPriorityList(currentPriorityName);

    menu.style.visibility = 'hidden';
    menu.style.display = 'block';

    const rect = btn.getBoundingClientRect();
    let top = rect.bottom + 4;
    let left = rect.left;
    if (left + menu.offsetWidth > window.innerWidth - 8) left = window.innerWidth - menu.offsetWidth - 8;
    if (top + menu.offsetHeight > window.innerHeight - 8) top = rect.top - menu.offsetHeight - 4;
    if (left < 8) left = 8;

    menu.style.top = top + 'px';
    menu.style.left = left + 'px';
    menu.style.visibility = 'visible';
}

function closePriorityMenu() {
    const menu = document.getElementById('priorityPickerMenu');
    if (menu) menu.style.display = 'none';
    window._priorityCurrentBtn = null;
}

// Close on outside click
document.addEventListener('click', (e) => {
    const menu = document.getElementById('priorityPickerMenu');
    if (!menu || menu.style.display === 'none' || menu.style.visibility === 'hidden') return;
    if (menu.contains(e.target)) return;
    if (e.target.closest('.card-priority-btn')) return;
    closePriorityMenu();
});

async function changePriority(ticketId, priorityName) {
    // Resolve priority ID: prefer PRIORITY_CONFIGS (patched from server),
    // then fall back to any card button that already has this priority.
    let priorityId = null;

    // 1. From PRIORITY_CONFIGS (patched by board.html inline script)
    const pConf = PRIORITY_CONFIGS.find(c => c.name === priorityName);
    if (pConf && pConf.id) priorityId = pConf.id;

    // 2. Fallback: any card button that already has this priority name → take its ID
    if (!priorityId) {
        document.querySelectorAll('.card-priority-btn').forEach(b => {
            if (!priorityId && b.dataset.priorityName === priorityName && b.dataset.priorityId) {
                priorityId = b.dataset.priorityId;
            }
        });
    }

    if (!priorityId) {
        alert('Could not determine priority ID. Please reload the page.');
        return;
    }

    try {
        const res = await fetch(`/api/tickets/${ticketId}/update-priority/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ priority_id: priorityId })
        });
        const data = await res.json();
        if (data.success) {
            // 1. Update card priority button icon + data attributes
            const cardBtn = document.querySelector(`.card-priority-btn[data-ticket-id="${ticketId}"]`);
            if (cardBtn) {
                cardBtn.dataset.priorityName = priorityName;
                cardBtn.dataset.priorityId = priorityId;
                cardBtn.innerHTML = getPriorityIcon(priorityName);
            }

            // 2. Update detail modal priority text (if open)
            const detailPriority = document.getElementById('detailPriority');
            if (detailPriority) {
                const addCommBtn = document.getElementById('addCommentBtn');
                if (addCommBtn && String(addCommBtn.dataset.ticketId) === String(ticketId)) {
                    detailPriority.textContent = priorityName;
                }
            }

            // 3. Update list-view prio trigger if present
            const listPrioContainer = document.querySelector(`.prio-dropdown-container[data-ticket-id="${ticketId}"]`);
            if (listPrioContainer) {
                const trigger = listPrioContainer.querySelector('.prio-select-value');
                if (trigger) {
                    const pConf = PRIORITY_CONFIGS.find(p => p.name === priorityName);
                    trigger.innerHTML = pConf ? `${pConf.icon}<span>${priorityName}</span>` : `<span>${priorityName}</span>`;
                }
                // Update selected state in dropdown items
                listPrioContainer.querySelectorAll('.prio-option-item').forEach(item => {
                    item.classList.toggle('selected', item.querySelector('span')?.textContent.trim() === priorityName);
                });
            }
        } else {
            alert('Failed to update priority: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error(err);
    }
}

window.openPriorityMenu = openPriorityMenu;

// ---------------- ADD USER ACCOUNT HANDLER ----------------
const addUserForm = document.getElementById('addUserForm');
if (addUserForm) {
    addUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const alertEl = document.getElementById('addUserAlert');
        const btnSubmit = document.getElementById('btnSubmitAddUser');
        
        const inputVal = document.getElementById('addEmailOrName') ? document.getElementById('addEmailOrName').value.trim() : '';
        const roleVal = document.getElementById('addRoleSelect') ? document.getElementById('addRoleSelect').value : 'Member';

        if (!inputVal) return;

        if (btnSubmit) { btnSubmit.disabled = true; btnSubmit.textContent = 'Adding...'; }

        try {
            const res = await fetch('/api/users/create/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    names_or_emails: inputVal,
                    role_name: roleVal
                })
            });
            const data = await res.json();
            if (data.success) {
                if (alertEl) {
                    alertEl.style.background = 'rgba(75, 179, 129, 0.15)';
                    alertEl.style.color = '#4bb381';
                    alertEl.textContent = `Success! Added ${data.user.full_name || data.user.username} as ${data.user.role}.`;
                    alertEl.style.display = 'block';
                }
                setTimeout(() => {
                    const modal = document.getElementById('addUserModal');
                    if (modal) modal.style.display = 'none';
                    addUserForm.reset();
                    if (alertEl) alertEl.style.display = 'none';
                    location.reload();
                }, 1000);
            } else {
                if (alertEl) {
                    alertEl.style.background = 'rgba(255, 86, 48, 0.15)';
                    alertEl.style.color = '#ff5630';
                    alertEl.textContent = data.error || 'Failed to add user.';
                    alertEl.style.display = 'block';
                }
            }
        } catch (err) {
            console.error(err);
        } finally {
            if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.textContent = 'Add'; }
        }
    });
}

// ---------------- EDIT TICKET FORM HANDLER ----------------
const editTicketForm = document.getElementById('editTicketForm');
if (editTicketForm) {
    editTicketForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const editModal = document.getElementById('editTicketModal');
        const ticketId = editModal ? editModal.dataset.ticketId : null;
        if (!ticketId) return;

        const alertEl = document.getElementById('editTicketAlert');
        const btnSubmit = document.getElementById('btnSubmitEditTicket');
        if (btnSubmit) { btnSubmit.disabled = true; btnSubmit.textContent = 'Saving...'; }

        const payload = {
            subject: document.getElementById('editSubject').value.trim(),
            description: document.getElementById('editDescription').value.trim(),
            assigned_to_id: document.getElementById('editAssignee') ? document.getElementById('editAssignee').value : '',
            priority_id: document.getElementById('editPriority') ? document.getElementById('editPriority').value : '',
            category_id: document.getElementById('editCategory') ? document.getElementById('editCategory').value : '',
            start_date: document.getElementById('editStartDate') ? document.getElementById('editStartDate').value : '',
            due_date: document.getElementById('editDueDate') ? document.getElementById('editDueDate').value : ''
        };

        try {
            const res = await fetch(`/api/tickets/${ticketId}/edit/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                closeEditTicketModal();
                if (window.openTicketDetailModal) {
                    window.openTicketDetailModal(ticketId);
                } else {
                    location.reload();
                }
            } else {
                if (alertEl) {
                    alertEl.style.background = 'rgba(255, 86, 48, 0.15)';
                    alertEl.style.color = '#ff5630';
                    alertEl.textContent = data.error || 'Failed to update ticket.';
                    alertEl.style.display = 'block';
                }
            }
        } catch (err) {
            console.error(err);
        } finally {
            if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.textContent = 'Save Changes'; }
        }
    });
}

// Inline Create Category Button Handler in Edit Modal
const btnAddCatEdit = document.getElementById('btnInlineAddCategoryEdit');
if (btnAddCatEdit) {
    btnAddCatEdit.addEventListener('click', async () => {
        const catName = prompt("Enter new category name:");
        if (!catName || !catName.trim()) return;
        try {
            const res = await fetch('/api/categories/create/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category_name: catName.trim() })
            });
            const data = await res.json();
            if (data.success) {
                const selectEl = document.getElementById('editCategory');
                if (selectEl) {
                    const opt = document.createElement('option');
                    opt.value = data.category_id;
                    opt.textContent = data.category_name;
                    opt.selected = true;
                    selectEl.appendChild(opt);
                }
            } else {
                alert(data.error || 'Failed to create category.');
            }
        } catch (err) {
            console.error(err);
            alert('Error creating category.');
        }
    });
}

