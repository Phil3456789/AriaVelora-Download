import webbrowser
import os
import sys
import tempfile

HTML_CONTENT = r'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Discord</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; transition: all 0.2s ease; }
        :root { --bg-primary: #313338; --bg-secondary: #2b2d31; --bg-tertiary: #1e1f22; --bg-hover: #3f4147; --text-normal: #dbdee1; --text-muted: #949ba4; --accent: #5865f2; --danger: #da373c; --success: #23a559; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg-primary); color: var(--text-normal); height: 100vh; overflow: hidden; display: flex; }
        @keyframes fadeIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        .fade-in { animation: fadeIn 0.2s ease; }
        .slide-up { animation: slideUp 0.2s ease; }
        .server-icon:hover { transform: scale(1.1); }
        .channel-item:hover { transform: translateX(4px); }
        .servers-nav { width: 72px; background: var(--bg-tertiary); display: flex; flex-direction: column; padding: 12px 8px; gap: 8px; overflow-y: auto; z-index: 1; }
        .server-icon { width: 48px; height: 48px; border-radius: 50%; background: var(--bg-primary); display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 20px; color: var(--text-normal); border: none; position: relative; }
        .server-icon:hover { border-radius: 16px; background: var(--accent); }
        .server-icon.active { border-radius: 16px; background: var(--accent); }
        .server-divider { height: 2px; background: var(--bg-hover); width: 32px; margin: 8px auto; border-radius: 1px; }
        .add-server { color: var(--success); }
        .add-server:hover { color: var(--text-normal); background: var(--success); }
        .owner-badge { position: absolute; top: -4px; right: -4px; background: #ff0000; color: white; font-size: 6px; padding: 2px 4px; border-radius: 4px; font-weight: bold; }
        .dm-sidebar { width: 240px; background: var(--bg-secondary); display: none; flex-direction: column; z-index: 1; }
        .dm-sidebar.active { display: flex; }
        .dm-header { padding: 16px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 0 var(--bg-tertiary); }
        .dm-header-btn { background: none; border: none; color: var(--text-muted); font-size: 18px; cursor: pointer; padding: 4px; }
        .dm-header-btn:hover { transform: scale(1.1); }
        .dm-list { flex: 1; overflow-y: auto; padding: 8px; }
        .dm-section-title { color: var(--text-muted); font-size: 12px; font-weight: bold; padding: 8px; text-transform: uppercase; }
        .notification-badge { background: var(--danger); color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; }
        .friend-item { display: flex; align-items: center; gap: 12px; padding: 8px; border-radius: 8px; cursor: pointer; }
        .friend-item:hover { background: var(--bg-hover); transform: translateX(4px); }
        .friend-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: bold; position: relative; }
        .friend-avatar img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        .friend-info { flex: 1; }
        .friend-name { font-weight: 500; display: flex; align-items: center; gap: 4px; }
        .friend-name.owner { color: #ff4444; font-weight: bold; }
        .friend-status { font-size: 12px; color: var(--text-muted); }
        .friend-voice { position: absolute; bottom: -2px; right: -2px; width: 12px; height: 12px; background: var(--success); border-radius: 50%; border: 2px solid var(--bg-secondary); }
        .friend-request { display: flex; flex-direction: column; gap: 8px; padding: 8px; background: var(--bg-hover); border-radius: 8px; margin-bottom: 8px; }
        .friend-request-btns { display: flex; gap: 8px; }
        .friend-request-btn { flex: 1; padding: 6px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .accept-btn { background: var(--success); color: white; }
        .decline-btn { background: var(--danger); color: white; }
        .channel-sidebar { width: 240px; background: var(--bg-secondary); display: flex; flex-direction: column; z-index: 1; }
        .channel-sidebar.hidden { display: none; }
        .channel-header { padding: 16px; font-weight: bold; display: flex; align-items: center; gap: 8px; box-shadow: 0 1px 0 var(--bg-tertiary); cursor: pointer; justify-content: space-between; }
        .channel-header:hover { background: var(--bg-hover); }
        .channel-header-actions { display: flex; gap: 4px; }
        .channel-header-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 4px; }
        .channel-list { flex: 1; overflow-y: auto; padding: 8px; }
        .channel-category { color: var(--text-muted); font-size: 12px; font-weight: bold; text-transform: uppercase; padding: 16px 8px 8px; display: flex; justify-content: space-between; align-items: center; }
        .channel-category-actions { display: flex; gap: 4px; }
        .channel-category-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 16px; }
        .channel-category-btn:hover { transform: scale(1.2); }
        .channel-item { display: flex; align-items: center; padding: 8px; border-radius: 4px; cursor: pointer; color: var(--text-muted); gap: 8px; margin-bottom: 2px; flex: 1; }
        .channel-item:hover { background: var(--bg-hover); color: var(--text-normal); }
        .channel-item.active { background: var(--bg-hover); color: var(--text-normal); }
        .channel-icon { font-size: 18px; }
        .channel-delete { display: none; background: none; border: none; color: var(--danger); cursor: pointer; font-size: 12px; padding: 2px; }
        .channel-item:hover .channel-delete { display: block; }
        .voice-channel { color: var(--success); }
        .voice-channel.joined { background: var(--bg-hover); }
        .voice-users { background: var(--bg-tertiary); padding: 8px; margin: 8px; border-radius: 8px; }
        .voice-users-title { font-size: 12px; color: var(--text-muted); font-weight: bold; margin-bottom: 8px; }
        .voice-user { display: flex; align-items: center; gap: 8px; padding: 6px; border-radius: 4px; }
        .voice-user:hover { background: var(--bg-hover); }
        .voice-user-avatar { width: 24px; height: 24px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; }
        .voice-user-name { font-size: 13px; flex: 1; }
        .control-btn { width: 32px; height: 32px; border-radius: 4px; border: none; background: var(--bg-hover); color: var(--text-normal); cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; }
        .control-btn:hover { background: var(--bg-primary); }
        .control-btn.active { background: var(--danger); color: white; }
        .user-panel { background: #232428; padding: 8px 12px; display: flex; align-items: center; gap: 8px; z-index: 1; }
        .user-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; position: relative; cursor: pointer; }
        .user-avatar img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        .user-info { flex: 1; }
        .user-name { font-weight: bold; font-size: 14px; display: flex; align-items: center; gap: 4px; }
        .user-name.owner { color: #ff4444; }
        .owner-tag { font-size: 10px; background: #ff0000; color: white; padding: 2px 4px; border-radius: 4px; }
        .user-status { font-size: 12px; color: var(--text-muted); }
        .user-btn { background: none; border: none; color: var(--text-muted); font-size: 18px; padding: 8px; cursor: pointer; border-radius: 4px; }
        .user-btn:hover { background: var(--bg-hover); color: var(--text-normal); transform: scale(1.1); }
        .chat-area { flex: 1; display: flex; flex-direction: column; background: var(--bg-primary); z-index: 1; }
        .chat-header { padding: 16px; border-bottom: 1px solid var(--bg-tertiary); display: flex; align-items: center; gap: 8px; font-weight: bold; box-shadow: 0 1px 0 var(--bg-tertiary); }
        .chat-header-icon { font-size: 24px; }
        .chat-header-title { flex: 1; }
        .chat-header-info { font-size: 14px; color: var(--text-muted); font-weight: normal; }
        .chat-header-btn { background: none; border: none; color: var(--text-muted); font-size: 24px; cursor: pointer; }
        .chat-header-btn:hover { transform: scale(1.1); }
        .call-buttons { display: flex; gap: 8px; }
        .call-btn { padding: 8px 16px; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; }
        .call-btn-video { background: var(--accent); color: white; }
        .call-btn-phone { background: var(--success); color: white; }
        .voice-indicator { display: flex; align-items: center; gap: 8px; background: var(--success); color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; }
        .messages { flex: 1; overflow-y: auto; padding: 16px; }
        .message { display: flex; gap: 16px; padding: 8px 0; position: relative; }
        .message:hover { background: var(--bg-secondary); margin: 0 -16px; padding: 8px 16px; }
        .message.deleted { opacity: 0.6; }
        .message.deleted .message-text { text-decoration: line-through; color: var(--danger); }
        .message-avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; cursor: pointer; position: relative; }
        .message-avatar img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        .message-content { flex: 1; min-width: 0; }
        .message-header { display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
        .message-username { font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 4px; }
        .message-username.owner { color: #ff4444; }
        .display-name { color: var(--text-muted); font-weight: normal; font-size: 12px; }
        .verified-icon { color: var(--accent); margin-left: 4px; }
        .owner-tag-msg { font-size: 10px; background: #ff0000; color: white; padding: 2px 4px; border-radius: 4px; }
        .message-time { font-size: 12px; color: var(--text-muted); }
        .message-id { font-size: 10px; color: var(--text-muted); background: var(--bg-hover); padding: 2px 6px; border-radius: 4px; cursor: pointer; }
        .message-text { color: var(--text-normal); word-wrap: break-word; }
        .message-text .mention { color: var(--accent); background: rgba(88,101,242,0.2); padding: 2px 6px; border-radius: 4px; cursor: pointer; }
        .message-img { max-width: 400px; max-height: 300px; border-radius: 8px; margin-top: 8px; }
        .reply-banner { background: var(--bg-hover); padding: 8px 16px; margin: 0 -16px 8px; border-left: 4px solid var(--accent); display: flex; align-items: center; gap: 8px; font-size: 13px; }
        .message-actions { display: none; position: absolute; right: 16px; top: 8px; background: var(--bg-secondary); border-radius: 4px; padding: 4px; gap: 4px; }
        .message:hover .message-actions { display: flex; }
        .message-action-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px 8px; border-radius: 4px; font-size: 14px; }
        .chat-input-area { padding: 16px 16px 24px; }
        .chat-input-wrapper { background: var(--bg-secondary); border-radius: 8px; padding: 12px 16px; display: flex; align-items: center; gap: 16px; }
        .chat-input-btn { background: none; border: none; font-size: 24px; color: var(--text-muted); cursor: pointer; padding: 4px; }
        .chat-input-btn:hover { transform: scale(1.1); color: var(--text-normal); }
        .chat-input { flex: 1; background: transparent; border: none; color: var(--text-normal); font-size: 15px; outline: none; }
        .chat-input::placeholder { color: var(--text-muted); }
        .welcome-screen { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .welcome-icon { font-size: 80px; margin-bottom: 16px; animation: pulse 2s infinite; }
        .welcome-title { font-size: 32px; font-weight: bold; margin-bottom: 8px; }
        .welcome-text { color: var(--text-muted); text-align: center; max-width: 400px; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 1000; }
        .modal.show { display: flex; }
        .modal-content { background: var(--bg-secondary); border-radius: 8px; padding: 24px; width: 420px; max-width: 90%; }
        .modal-title { font-size: 20px; font-weight: bold; margin-bottom: 16px; }
        .modal-input { width: 100%; padding: 12px; background: var(--bg-primary); border: none; border-radius: 4px; color: var(--text-normal); font-size: 16px; margin-bottom: 16px; }
        .modal-input:focus { outline: 2px solid var(--accent); }
        .modal-btn { background: var(--accent); color: white; border: none; padding: 12px 24px; border-radius: 4px; font-weight: bold; cursor: pointer; width: 100%; }
        .modal-btn:hover { transform: scale(1.02); }
        .modal-btn-danger { background: var(--danger); }
        .settings-dropdown { position: relative; }
        .settings-menu { display: none; position: absolute; bottom: 100%; right: 0; background: var(--bg-secondary); border-radius: 8px; padding: 8px; margin-bottom: 8px; min-width: 220px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); z-index: 100; }
        .settings-menu.show { display: block; animation: slideUp 0.2s ease; }
        .settings-item { padding: 8px 12px; border-radius: 4px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .settings-item:hover { background: var(--bg-hover); transform: translateX(4px); }
        .theme-colors { display: flex; gap: 8px; padding: 8px; flex-wrap: wrap; }
        .theme-color { width: 28px; height: 28px; border-radius: 4px; cursor: pointer; border: 2px solid transparent; }
        .theme-color:hover { transform: scale(1.1); border-color: var(--text-normal); }
        .bottom-tabs { display: flex; gap: 4px; padding: 8px; border-top: 1px solid var(--bg-tertiary); }
        .bottom-tab { flex: 1; padding: 8px; border-radius: 4px; text-align: center; cursor: pointer; color: var(--text-muted); font-size: 12px; }
        .bottom-tab:hover { background: var(--bg-hover); color: var(--text-normal); }
        .bottom-tab.active { background: var(--bg-hover); color: var(--text-normal); }
        .bottom-tab-icon { font-size: 20px; margin-bottom: 4px; display: block; }
        .back-btn { background: none; border: none; color: var(--text-muted); font-size: 20px; cursor: pointer; padding: 8px; margin-right: 8px; }
        .back-btn:hover { transform: scale(1.1); color: var(--text-normal); }
        .profile-modal { text-align: center; }
        .profile-avatar { width: 80px; height: 80px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; margin: 0 auto 16px; position: relative; }
        .profile-avatar img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        .profile-name { font-size: 24px; font-weight: bold; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .profile-name.owner { color: #ff4444; }
        .profile-username { color: var(--text-muted); font-size: 16px; margin-bottom: 16px; }
        .profile-id { font-size: 12px; color: var(--text-muted); background: var(--bg-hover); padding: 4px 8px; border-radius: 4px; display: inline-block; }
        .autocomplete { display: none; position: absolute; background: var(--bg-secondary); border-radius: 4px; padding: 4px; max-height: 150px; overflow-y: auto; z-index: 100; }
        .autocomplete.show { display: block; animation: slideUp 0.15s ease; }
        .autocomplete-item { padding: 8px; cursor: pointer; border-radius: 4px; }
        .autocomplete-item:hover { background: var(--bg-hover); transform: translateX(4px); }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-secondary); }
        ::-webkit-scrollbar-thumb { background: var(--bg-hover); border-radius: 4px; }
        .dev-panel { display: none; position: fixed; top: 0; right: 0; width: 300px; height: 100%; background: #1a1a1a; border-left: 2px solid red; padding: 16px; z-index: 1000; overflow-y: auto; }
        .dev-panel.show { display: block; animation: slideUp 0.3s ease; }
        .dev-title { color: red; font-weight: bold; margin-bottom: 16px; font-size: 18px; }
        .dev-section { margin-bottom: 16px; }
        .dev-section-title { color: #ff6666; font-weight: bold; margin-bottom: 8px; }
        .dev-btn { background: #333; color: white; border: none; padding: 8px; border-radius: 4px; cursor: pointer; width: 100%; margin-bottom: 8px; }
        .dev-btn:hover { transform: scale(1.02); }
    </style>
</head>
<body>
    <div class="servers-nav">
        <button class="server-icon" onclick="goBack()">⬅️</button>
        <button class="server-icon dm-btn" onclick="switchView('dms')">💬</button>
        <div class="server-divider"></div>
        <div id="serverList"></div>
        <div class="server-divider"></div>
        <button class="server-icon add-server" onclick="showModal('createServerModal')">+</button>
    </div>
    <div class="dm-sidebar" id="dmSidebar">
        <div class="dm-header fade-in"><span>Direct Messages</span><button class="dm-header-btn" onclick="showModal('newDmModal')">+</button></div>
        <div class="dm-list">
            <div class="dm-section-title">Friend Requests <span id="friendRequestBadge" class="notification-badge" style="display:none">0</span></div>
            <div id="friendRequests"></div>
            <div class="dm-section-title">Friends</div>
            <div id="friendsList"></div>
            <div class="dm-section-title">Group DM</div>
            <div id="groupDMs"></div>
            <button class="channel-item" onclick="showModal('createGroupModal')" style="width:100%;margin-top:8px;"><span>+</span><span>Create Group</span></button>
        </div>
        <div class="user-panel">
            <div class="user-avatar" id="userAvatar" onclick="showProfileModal()">
                <img id="userAvatarImg" style="display:none">
                <span id="userAvatarText">U</span>
                <div id="ownerBadge" class="owner-badge" style="display:none">OWNER</div>
            </div>
            <div class="user-info">
                <div class="user-name" id="userName">User</div>
                <div class="user-status" id="userIdDisplay">Click for profile</div>
            </div>
            <div class="settings-dropdown">
                <button class="user-btn" onclick="toggleSettings()">⚙️</button>
                <div class="settings-menu" id="settingsMenu">
                    <div class="settings-item" onclick="showModal('avatarModal'); hideSettings();"><span>📷</span> Set Avatar</div>
                    <div class="settings-item" onclick="showModal('usernameModal'); hideSettings();"><span>👤</span> Set Username</div>
                    <div class="settings-item" onclick="showModal('displayNameModal'); hideSettings();"><span>📝</span> Set Display Name</div>
                    <div class="settings-item" onclick="showModal('passwordModal'); hideSettings();"><span>🔐</span> Set Password</div>
                    <div class="settings-item" onclick="showModal('devModal'); hideSettings();"><span>🔧</span> Dev Menu</div>
                    <div class="settings-item"><span>🎨</span> Themes<div class="theme-colors">
                        <div class="theme-color" style="background:#313338" onclick="setTheme('dark')" title="Dark"></div>
                        <div class="theme-color" style="background:#f2f3f5" onclick="setTheme('light')" title="Light"></div>
                        <div class="theme-color" style="background:#3d2e2e" onclick="setTheme('sunset')" title="Sunset"></div>
                        <div class="theme-color" style="background:#1e3a5f" onclick="setTheme('ocean')" title="Ocean"></div>
                        <div class="theme-color" style="background:#1a1a2e" onclick="setTheme('midnight')" title="Midnight"></div>
                        <div class="theme-color" style="background:#2d1b1b" onclick="setTheme('wine')" title="Wine"></div>
                        <div class="theme-color" style="background:#1a2f1a" onclick="setTheme('forest')" title="Forest"></div>
                        <div class="theme-color" style="background:#2b1a4e" onclick="setTheme('purple')" title="Purple"></div>
                    </div></div>
                    <div class="settings-item" onclick="showModal('roomModal'); hideSettings();"><span>🔗</span> Join Room</div>
                </div>
            </div>
        </div>
    </div>
    <div class="channel-sidebar" id="channelSidebar">
        <div class="channel-header" onclick="selectServer(currentServer)">
            <span id="serverIcon">🎮</span>
            <span id="serverName">Main Server</span>
            <div class="channel-header-actions" id="serverActions" style="display:none">
                <button class="channel-header-btn" onclick="showInvite(event)" title="Invite">🔗</button>
                <button class="channel-header-btn" id="deleteServerBtn" onclick="deleteServer(event)" title="Delete Server" style="color:var(--danger)">🗑️</button>
            </div>
        </div>
        <div class="channel-list" id="channelList"></div>
        <div class="voice-users" id="voiceUsersSection" style="display:none">
            <div class="voice-users-title">🔊 Voice Chat</div>
            <div id="voiceUsersList"></div>
            <div style="display:flex;gap:4px;margin-top:8px">
                <button class="control-btn" id="muteBtn" onclick="toggleMute()" title="Mute">🔇</button>
                <button class="control-btn" id="deafenBtn" onclick="toggleDeafen()" title="Deafen">🔊</button>
                <button class="control-btn" onclick="leaveVoice()" title="Leave">📴</button>
            </div>
        </div>
        <div class="bottom-tabs">
            <div class="bottom-tab" data-view="servers" onclick="switchView('servers')"><span class="bottom-tab-icon">🏠</span>Servers</div>
            <div class="bottom-tab" data-view="dms" onclick="switchView('dms')"><span class="bottom-tab-icon">💬</span>DMs</div>
            <div class="bottom-tab" data-view="friends" onclick="switchView('friends')"><span class="bottom-tab-icon">👥</span>Friends</div>
        </div>
        <div class="user-panel">
            <div class="user-avatar" id="userAvatar2" onclick="showProfileModal()">
                <img id="userAvatarImg2" style="display:none">
                <span id="userAvatarText2">U</span>
                <div id="ownerBadge2" class="owner-badge" style="display:none">OWNER</div>
            </div>
            <div class="user-info">
                <div class="user-name" id="userName2">User</div>
                <div class="user-status">Online</div>
            </div>
            <button class="user-btn" onclick="toggleSettings()">⚙️</button>
        </div>
    </div>
    <div class="chat-area">
        <div class="chat-header">
            <button class="back-btn" onclick="goBack()" style="display:none" id="backBtn">⬅️</button>
            <span class="chat-header-icon" id="chatIcon">#</span>
            <div class="chat-header-title"><span id="chatName">general</span><span class="chat-header-info" id="chatInfo"></span></div>
            <div id="voiceIndicator" style="display:none" class="voice-indicator">🔊 In Voice</div>
            <div class="chat-header-actions">
                <div class="call-buttons" id="callButtons" style="display:none">
                    <button class="call-btn call-btn-video" onclick="startVideoCall()">📹 Video</button>
                    <button class="call-btn call-btn-phone" onclick="startCall()">📞 Call</button>
                </div>
                <button class="chat-header-btn">📌</button>
                <button class="chat-header-btn">👥</button>
            </div>
        </div>
        <div id="welcomeScreen" class="welcome-screen">
            <div class="welcome-icon">💬</div>
            <div class="welcome-title">Welcome!</div>
            <div class="welcome-text">Select a channel to start chatting.</div>
        </div>
        <div class="messages" id="messages" style="display:none"></div>
        <div class="chat-input-area" id="inputArea" style="display:none">
            <div class="reply-banner" id="replyBanner" style="display:none">
                <span>Replying to <strong id="replyToUser"></strong></span>
                <button class="reply-banner-cancel" onclick="cancelReply()">✕</button>
            </div>
            <div style="position:relative">
                <div class="chat-input-wrapper">
                    <button class="chat-input-btn" onclick="document.getElementById('fileInput').click()" title="Send Image">➕</button>
                    <input type="text" class="chat-input" id="msgInput" placeholder="Message #general">
                    <button class="chat-input-btn" onclick="sendMessage()" title="Send" style="font-size:14px;font-weight:bold">Send</button>
                    <button class="chat-input-btn" onclick="showGifModal()" title="Add GIF">🎁</button>
                    <button class="chat-input-btn" onclick="showEmojiModal()" title="Emojis">😀</button>
                </div>
                <div id="autocomplete" class="autocomplete"></div>
            </div>
        </div>
    </div>
    <div class="modal" id="usernameModal"><div class="modal-content"><div class="modal-title">Choose a Username</div><p style="color:var(--text-muted);margin-bottom:16px;font-size:14px">Create your account</p><input type="text" class="modal-input" id="usernameInput" placeholder="Enter username" maxlength="20"><input type="password" class="modal-input" id="newPasswordInput" placeholder="Set password (min 8 chars)"><input type="password" class="modal-input" id="newConfirmPasswordInput" placeholder="Confirm password"><button class="modal-btn" onclick="saveUsername()">Create Account</button></div></div>
    <div class="modal" id="displayNameModal"><div class="modal-content"><div class="modal-title">Set Display Name</div><input type="text" class="modal-input" id="displayNameInput" placeholder="Display name (shown in servers)" maxlength="20"><button class="modal-btn" onclick="saveDisplayName()">Save</button></div></div>
    <div class="modal" id="passwordModal"><div class="modal-content"><div class="modal-title">Set Password</div><input type="password" class="modal-input" id="passwordInput" placeholder="Enter password (min 8 chars)"><input type="password" class="modal-input" id="confirmPasswordInput" placeholder="Confirm password"><button class="modal-btn" onclick="savePassword()">Save</button></div></div>
    <div class="modal" id="avatarModal"><div class="modal-content"><div class="modal-title">Set Avatar</div><input type="file" class="modal-input" id="avatarInput" accept="image/*"><button class="modal-btn" onclick="saveAvatar()">Save</button></div></div>
    <div class="modal" id="roomModal"><div class="modal-content"><div class="modal-title">Join Room</div><input type="text" class="modal-input" id="roomInput" placeholder="Room name"><button class="modal-btn" onclick="joinRoom()">Join</button></div></div>
    <div class="modal" id="newDmModal"><div class="modal-content"><div class="modal-title">New Message</div><input type="text" class="modal-input" id="newDmInput" placeholder="Username to message"><input type="password" class="modal-input" id="newDmPassword" placeholder="Your password"><button class="modal-btn" onclick="createDM()">Start Chat</button></div></div>
    <div class="modal" id="createServerModal"><div class="modal-content"><div class="modal-title">Create Server</div><input type="text" class="modal-input" id="serverNameInput" placeholder="Server name"><button class="modal-btn" onclick="createServer()">Create</button></div></div>
    <div class="modal" id="createGroupModal"><div class="modal-content"><div class="modal-title">Create Group</div><input type="text" class="modal-input" id="groupNameInput" placeholder="Group name"><input type="text" class="modal-input" id="groupMembersInput" placeholder="Members (comma separated)"><button class="modal-btn" onclick="createGroup()">Create</button></div></div>
    <div class="modal" id="addFriendModal"><div class="modal-content"><div class="modal-title">Add Friend</div><input type="text" class="modal-input" id="friendNameInput" placeholder="Enter username"><button class="modal-btn" onclick="addFriend()">Send Request</button></div></div>
    <div class="modal" id="createChannelModal"><div class="modal-content"><div class="modal-title">Create Channel</div><input type="text" class="modal-input" id="channelNameInput" placeholder="Channel name"><button class="modal-btn" onclick="createChannel()">Create</button></div></div>
    <div class="modal" id="emojiModal"><div class="modal-content" style="width:320px"><div class="modal-title">Emojis</div><div style="display:grid;grid-template-columns:repeat(8,1fr);gap:4px;max-height:200px;overflow-y:auto" id="emojiGrid"></div></div></div>
    <div class="modal" id="gifModal"><div class="modal-content" style="width:400px"><div class="modal-title">Add GIF</div><input type="text" class="modal-input" id="gifSearch" placeholder="Search GIFs"><button class="modal-btn" onclick="searchGifs()" style="margin-bottom:12px">Search</button><div id="gifResults" style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;max-height:250px;overflow-y:auto"></div></div></div>
    <div class="modal" id="profileModal"><div class="modal-content profile-modal">
        <div class="profile-avatar" id="profileAvatar">
            <img id="profileAvatarImg" style="display:none">
            <span id="profileAvatarText">U</span>
        </div>
        <div class="profile-name" id="profileName">User <span class="owner-tag" id="profileOwnerTag" style="display:none">Main Developer & Owner</span></div>
        <div class="profile-username" id="profileUsername">@username</div>
        <div class="profile-id" id="profileId">ID: click to copy</div>
        <button class="modal-btn" style="margin-top:16px" onclick="hideModal('profileModal')">Close</button>
    </div></div>
    <div class="modal" id="devModal"><div class="modal-content"><div class="modal-title">Developer Access</div><input type="text" class="modal-input" id="devUsername" placeholder="Username"><input type="password" class="modal-input" id="devPassword" placeholder="Password"><button class="modal-btn" onclick="checkDevAuth()">Login</button></div></div>
    <div class="dev-panel" id="devPanel">
        <div class="dev-title">Developer Panel</div>
        <div class="dev-section"><div class="dev-section-title">Owner Actions</div>
            <button class="dev-btn" onclick="devDeleteAnyMessage()">Delete Any Message</button>
            <button class="dev-btn" onclick="devClearMessages()">Clear All Messages</button>
        </div>
        <div class="dev-section"><div class="dev-section-title">Server Management</div>
            <button class="dev-btn" onclick="showModal('createChannelModal')">Create Channel</button>
            <button class="dev-btn modal-btn-danger" onclick="deleteServer(null)">Delete Current Server</button>
        </div>
        <div class="dev-section"><button class="dev-btn modal-btn-danger" onclick="exitDevMode()">Exit Dev Mode</button></div>
    </div>
    <input type="file" id="fileInput" accept="image/*" style="display:none">
    <script>
        const API_KEY = '';
        
        let localStream = null, peerConnections = {}, isMuted = false, isDeafened = false;
        let voiceUsers = {};
        let username = localStorage.getItem('username') || '';
        let displayName = localStorage.getItem('displayName') || '';
        let userId = localStorage.getItem('userId') || ('id_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now());
        let userPassword = localStorage.getItem('userPassword') || '';
        let userAvatar = localStorage.getItem('userAvatar') || '';
        let roomName = localStorage.getItem('room') || 'global';
let serverUrl = window.location.origin;
        let currentView = 'servers', currentServer = '1', currentChannel = 'general', currentDM = null, replyingTo = null, client = null, inVoice = false;
        let messages = {};
        let deletedMessages = [];
        let verifiedUsers = JSON.parse(localStorage.getItem('verified_users') || '{}');
        let friends = JSON.parse(localStorage.getItem('friends') || '["Alice","Bob","Charlie"]');
        let friendRequests = JSON.parse(localStorage.getItem('friendRequests') || '[]');
        let groups = JSON.parse(localStorage.getItem('groups') || '[]');
        let servers = JSON.parse(localStorage.getItem('servers') || '{"1":{"name":"Main Server","icon":"🎮","channels":[{"name":"general","type":"text"},{"name":"Voice","type":"voice"},{"name":"announcements","type":"text"},{"name":"gaming","type":"text"}],"owner":"im.phil_real"},"2":{"name":"Tech Talk","icon":"💻","channels":[{"name":"general","type":"text"},{"name":"Voice","type":"voice"},{"name":"programming","type":"text"}],"owner":"im.phil_real"}}');
        let serverCount = Object.keys(servers).length;
        let isOwner = username === 'im.phil_real';
        
        localStorage.setItem('userId', userId);
        
        function checkOwner() {
            isOwner = username.toLowerCase() === 'im.phil_real';
            if (isOwner) {
                document.getElementById('ownerBadge').style.display = 'block';
                document.getElementById('ownerBadge2').style.display = 'block';
                document.getElementById('userName').classList.add('owner');
                document.getElementById('userName2').classList.add('owner');
            }
        }
        
        function saveMessages() {
            localStorage.setItem('verified_users', JSON.stringify(verifiedUsers));
            localStorage.setItem('friends', JSON.stringify(friends));
            localStorage.setItem('friendRequests', JSON.stringify(friendRequests));
            localStorage.setItem('groups', JSON.stringify(groups));
            localStorage.setItem('servers', JSON.stringify(servers));
            localStorage.setItem('deleted_messages', JSON.stringify(deletedMessages));
        }
        
        async function syncWithServer() {
            renderMessages();
            try {
                const key = currentServer + '_' + currentChannel;
                const response = await fetch(serverUrl + '/api/messages?server=' + currentServer + '&channel=' + currentChannel);
                if (response.ok) {
                    const serverMessages = await response.json();
                    messages[key] = serverMessages;
                    saveMessages();
                    renderMessages();
                }
            } catch(e) { console.log('Server sync failed:', e); }
        }
        
        async function syncServersFromServer() {
            try {
                const response = await fetch(serverUrl + '/api/servers');
                if (response.ok) {
                    const serverData = await response.json();
                    if (serverData && Object.keys(serverData).length > 0) {
                        servers = serverData;
                        saveMessages();
                        loadServers();
                        loadChannels();
                    }
                }
            } catch(e) { console.log('Server sync failed'); }
        }
        
        async function saveServersToServer() {
            try {
                await fetch(serverUrl + '/api/servers', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', 'Authorization': API_KEY},
                    body: JSON.stringify(servers)
                });
            } catch(e) { console.log('Server save failed'); }
        }
        
        async function saveToServer(msg) {
            try {
                await fetch(serverUrl + '/api/messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', 'Authorization': API_KEY},
                    body: JSON.stringify(msg)
                });
            } catch(e) { console.log('Server save failed'); }
        }
        
        function init() {
            syncServersFromServer();
            loadUsername();
            loadServers();
            loadChannels();
            loadFriends();
            loadFriendRequests();
            if (!username) showModal('usernameModal');
            connectToRoom(roomName);
            syncWithServer();
            checkOwner();
        }
        
        function loadUsername() {
            if (username) {
                const name = displayName || username;
                document.getElementById('userName').innerHTML = isOwner ? name + ' <span class="owner-tag">Main Developer & Owner</span>' : name;
                document.getElementById('userName2').innerHTML = isOwner ? name + ' <span class="owner-tag">Main Developer & Owner</span>' : name;
                document.getElementById('userIdDisplay').textContent = 'Click for profile';
                
                if (userAvatar) {
                    document.getElementById('userAvatarImg').src = userAvatar;
                    document.getElementById('userAvatarImg').style.display = 'block';
                    document.getElementById('userAvatarText').style.display = 'none';
                    document.getElementById('userAvatarImg2').src = userAvatar;
                    document.getElementById('userAvatarImg2').style.display = 'block';
                    document.getElementById('userAvatarText2').style.display = 'none';
                } else {
                    document.getElementById('userAvatarText').textContent = username.charAt(0).toUpperCase();
                    document.getElementById('userAvatarText2').textContent = username.charAt(0).toUpperCase();
                }
            }
        }
        
        function saveAvatar() {
            const file = document.getElementById('avatarInput').files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    userAvatar = e.target.result;
                    localStorage.setItem('userAvatar', userAvatar);
                    loadUsername();
                    hideModal('avatarModal');
                };
                reader.readAsDataURL(file);
            }
        }
        
        function saveDisplayName() {
            const name = document.getElementById('displayNameInput').value.trim();
            displayName = name;
            localStorage.setItem('displayName', name);
            loadUsername();
            hideModal('displayNameModal');
        }
        
        function savePassword() {
            const pass = document.getElementById('passwordInput').value;
            const confirm = document.getElementById('confirmPasswordInput').value;
            if (pass.length < 8) { alert('Password must be at least 8 characters!'); return; }
            if (pass !== confirm) { alert('Passwords do not match'); return; }
            userPassword = pass;
            verifiedUsers[username] = pass;
            localStorage.setItem('userPassword', pass);
            saveMessages();
            hideModal('passwordModal');
            alert('Password set!');
        }
        
        function loadServers() {
            const container = document.getElementById('serverList');
            container.innerHTML = '';
            Object.keys(servers).forEach(id => {
                const server = servers[id];
                const div = document.createElement('button');
                div.className = 'server-icon' + (id === currentServer ? ' active' : '');
                div.dataset.server = id;
                div.textContent = server.icon;
                div.onclick = () => selectServer(id);
                container.appendChild(div);
            });
        }
        
        function loadChannels() {
            const server = servers[currentServer];
            if (!server) return;
            
            let html = '<div class="channel-category"><span>Voice Channels</span></div>';
            server.channels.filter(c => c.type === 'voice').forEach(ch => {
                const joined = voiceUsers[currentServer]?.includes(ch.name) ? 'joined' : '';
                html += '<div class="channel-item voice-channel ' + joined + '" onclick="joinVoice(\'' + ch.name + '\')"><span class="channel-icon">🔊</span>' + ch.name + '</div>';
            });
            
            html += '<div class="channel-category"><span>Text Channels</span><div class="channel-category-actions">';
            if (isOwner) html += '<button class="channel-category-btn" onclick="showModal(\'createChannelModal\')">+</button>';
            html += '</div></div>';
            
            server.channels.filter(c => c.type === 'text').forEach(ch => {
                const deleteBtn = isOwner ? '<button class="channel-delete" onclick="deleteChannel(event, \'' + ch.name + '\')">🗑️</button>' : '';
                html += '<div class="channel-item ' + (ch.name === currentChannel ? 'active' : '') + '" onclick="selectChannel(\'' + ch.name + '\')"><span class="channel-icon">#</span>' + ch.name + deleteBtn + '</div>';
            });
            
            document.getElementById('channelList').innerHTML = html;
            document.getElementById('serverName').textContent = server.name;
            document.getElementById('serverIcon').textContent = server.icon;
            document.getElementById('serverActions').style.display = isOwner ? 'flex' : 'none';
        }
        
        function deleteChannel(event, channelName) {
            event.stopPropagation();
            if (!isOwner) return;
            if (confirm('Delete channel #' + channelName + '?')) {
                servers[currentServer].channels = servers[currentServer].channels.filter(c => c.name !== channelName);
                saveMessages();
                if (currentChannel === channelName) {
                    currentChannel = servers[currentServer].channels.find(c => c.type === 'text')?.name || 'general';
                }
                loadChannels();
            }
        }
        
        function deleteServer(event) {
            if (event) event.stopPropagation();
            if (!isOwner) return;
            if (confirm('Delete server "' + servers[currentServer].name + '"? This cannot be undone!')) {
                delete servers[currentServer];
                saveMessages();
                currentServer = Object.keys(servers)[0] || '1';
                if (!servers[currentServer]) {
                    serverCount++;
                    servers[currentServer] = {name: 'New Server', icon: '🎮', channels: [{name:'general',type:'text'},{name:'Voice',type:'voice'}], owner: 'im.phil_real'};
                }
                currentChannel = servers[currentServer].channels.find(c => c.type === 'text').name;
                loadServers();
                loadChannels();
            }
        }
        
        function showInvite(event) {
            event.stopPropagation();
            const inviteCode = btoa(currentServer + '-' + Date.now()).replace(/=/g, '').substring(0, 8);
            const inviteLink = serverUrl + '?invite=' + inviteCode;
            prompt('Share this invite link:', inviteLink);
        }
        
        function loadVoiceUsers() {
            const section = document.getElementById('voiceUsersSection');
            const list = document.getElementById('voiceUsersList');
            const users = voiceUsers[currentServer] || [];
            if (users.length > 0 || inVoice) {
                section.style.display = 'block';
                let html = '';
                if (inVoice) {
                    const avatarHtml = userAvatar ? '<img src="' + userAvatar + '" style="width:100%;height:100%;border-radius:50%;object-fit:cover">' : username.charAt(0).toUpperCase();
                    html += '<div class="voice-user"><div class="voice-user-avatar">' + avatarHtml + '</div><span class="voice-user-name">' + (displayName || username) + '</span><span class="voice-user-status">' + (isMuted ? '🔇' : '🎤') + '</span></div>';
                }
                users.forEach(u => {
                    if (u !== username) html += '<div class="voice-user"><div class="voice-user-avatar">' + u.charAt(0).toUpperCase() + '</div><span class="voice-user-name">' + u + '</span></div>';
                });
                list.innerHTML = html;
            } else {
                section.style.display = 'none';
            }
        }
        
        function joinVoice(channelName) {
            if (!voiceUsers[currentServer]) voiceUsers[currentServer] = [];
            if (!voiceUsers[currentServer].includes(username)) voiceUsers[currentServer].push(username);
            inVoice = true;
            document.getElementById('voiceIndicator').style.display = 'flex';
            loadChannels();
            loadVoiceUsers();
        }
        
        function leaveVoice() {
            if (voiceUsers[currentServer]) voiceUsers[currentServer] = voiceUsers[currentServer].filter(u => u !== username);
            inVoice = false;
            document.getElementById('voiceIndicator').style.display = 'none';
            loadChannels();
            loadVoiceUsers();
        }
        
        function toggleMute() { isMuted = !isMuted; document.getElementById('muteBtn').classList.toggle('active', isMuted); loadVoiceUsers(); }
        function toggleDeafen() { isDeafened = !isDeafened; document.getElementById('deafenBtn').classList.toggle('active', isDeafened); loadVoiceUsers(); }
        
        function showProfileModal() {
            const isVerified = verifiedUsers[username];
            const userIsOwner = username.toLowerCase() === 'im.phil_real';
            
            if (userAvatar) {
                document.getElementById('profileAvatarImg').src = userAvatar;
                document.getElementById('profileAvatarImg').style.display = 'block';
                document.getElementById('profileAvatarText').style.display = 'none';
            } else {
                document.getElementById('profileAvatarText').textContent = username.charAt(0).toUpperCase();
            }
            
            document.getElementById('profileName').innerHTML = (displayName || username) + (isVerified ? ' <span class="verified-icon">✓</span>' : '') + (userIsOwner ? ' <span class="owner-tag">Main Developer & Owner</span>' : '');
            document.getElementById('profileName').className = 'profile-name' + (userIsOwner ? ' owner' : '');
            document.getElementById('profileUsername').textContent = '@' + username;
            document.getElementById('profileId').textContent = 'ID: ' + userId;
            document.getElementById('profileId').onclick = function() { navigator.clipboard.writeText(userId); alert('User ID copied!'); };
            document.getElementById('profileOwnerTag').style.display = userIsOwner ? 'inline' : 'none';
            showModal('profileModal');
        }
        
        function loadFriends() {
            let html = '<button class="channel-item" onclick="showModal(\'addFriendModal\')" style="width:100%;margin-bottom:8px;"><span>+</span><span>Add Friend</span></button>';
            friends.forEach(friend => {
                const isVerified = verifiedUsers[friend];
                const isFriendOwner = friend.toLowerCase() === 'im.phil_real';
                const inCall = Object.values(voiceUsers).some(v => v.includes(friend));
                const nameClass = isFriendOwner ? 'owner' : '';
                html += '<div class="friend-item" onclick="openDM(\'' + friend + '\')"><div class="friend-avatar">' + friend.charAt(0) + (inCall ? '<span class="friend-voice"></span>' : '') + '</div><div class="friend-info"><div class="friend-name ' + nameClass + '">' + friend + (isVerified ? '<span class="verified-icon">✓</span>' : '') + '</div><div class="friend-status">' + (isFriendOwner ? 'Main Developer & Owner' : (isVerified ? 'Verified' : 'Not verified')) + '</div></div></div>';
            });
            document.getElementById('friendsList').innerHTML = html;
            
            let groupHtml = '';
            groups.forEach(group => {
                groupHtml += '<div class="friend-item" onclick="openGroup(\'' + group.name + '\')"><div class="friend-avatar">' + group.name.charAt(0) + '</div><div class="friend-info"><div class="friend-name">' + group.name + '</div><div class="friend-status">' + group.members.length + ' members</div></div></div>';
            });
            document.getElementById('groupDMs').innerHTML = groupHtml;
        }
        
        function loadFriendRequests() {
            const container = document.getElementById('friendRequests');
            const badge = document.getElementById('friendRequestBadge');
            if (friendRequests.length === 0) {
                container.innerHTML = '<div style="color:var(--text-muted);padding:8px;font-size:13px">No pending requests</div>';
                badge.style.display = 'none';
                return;
            }
            badge.style.display = 'inline';
            badge.textContent = friendRequests.length;
            let html = '';
            friendRequests.forEach((req, index) => {
                html += '<div class="friend-request"><div class="friend-request-name">' + req + '</div><div class="friend-request-btns"><button class="friend-request-btn accept-btn" onclick="acceptFriend(\'' + req + '\',' + index + ')">Accept</button><button class="friend-request-btn decline-btn" onclick="declineFriend(\'' + req + '\',' + index + ')">Decline</button></div></div>';
            });
            container.innerHTML = html;
        }
        
        function switchView(view) {
            currentView = view;
            document.querySelectorAll('.bottom-tab').forEach(t => t.classList.toggle('active', t.dataset.view === view));
            document.getElementById('dmSidebar').classList.toggle('active', view === 'dms' || view === 'friends');
            document.getElementById('channelSidebar').classList.toggle('hidden', view !== 'servers');
            document.getElementById('backBtn').style.display = view !== 'servers' ? 'block' : 'none';
            document.getElementById('callButtons').style.display = (view === 'dms' || view === 'friends') ? 'flex' : 'none';
        }
        
        function goBack() { switchView('servers'); }
        
        function selectServer(serverId) {
            currentServer = serverId;
            currentChannel = servers[serverId].channels.find(c => c.type === 'text').name;
            currentDM = null;
            document.querySelectorAll('.server-icon[data-server]').forEach(btn => btn.classList.toggle('active', btn.dataset.server === serverId));
            loadChannels();
            loadVoiceUsers();
            showWelcome();
            switchView('servers');
        }
        
        function selectChannel(channelId) { currentChannel = channelId; currentDM = null; document.getElementById('chatName').textContent = '# ' + channelId; document.getElementById('chatIcon').textContent = '#'; document.getElementById('chatInfo').textContent = ''; showChat(); renderMessages(); }
        function openDM(user) { currentDM = user; currentChannel = null; document.getElementById('chatName').textContent = user; document.getElementById('chatIcon').textContent = ''; document.getElementById('chatInfo').textContent = ' DM'; showChat(); renderMessages(); }
        function openGroup(groupName) { currentDM = groupName; currentChannel = null; document.getElementById('chatName').textContent = groupName; document.getElementById('chatIcon').textContent = ''; document.getElementById('chatInfo').textContent = ' Group'; showChat(); renderMessages(); }
        function showWelcome() { document.getElementById('welcomeScreen').style.display = 'flex'; document.getElementById('messages').style.display = 'none'; document.getElementById('inputArea').style.display = 'none'; }
        function showChat() { document.getElementById('welcomeScreen').style.display = 'none'; document.getElementById('messages').style.display = 'block'; document.getElementById('inputArea').style.display = 'block'; document.getElementById('msgInput').placeholder = currentDM ? 'Message @' + currentDM : 'Message #' + currentChannel; }
        
        function processMentions(text) {
            let result = text;
            friends.forEach(friend => {
                const regex = new RegExp('@' + friend, 'gi');
                result = result.replace(regex, '<span class="mention" onclick="openDM(\'' + friend + '\')">@' + friend + '</span>');
            });
            return result;
        }
        
        function renderMessages() {
            const key = currentDM ? 'dm_' + currentDM : currentServer + '_' + currentChannel;
            const msgs = messages[key] || [];
            document.getElementById('messages').innerHTML = '';
            
            msgs.forEach(msg => {
                const isDeleted = deletedMessages.includes(msg.id);
                const div = document.createElement('div');
                div.className = 'message' + (isDeleted ? ' deleted' : '');
                div.dataset.id = msg.id;
                const time = new Date(msg.time).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
                const isVerified = verifiedUsers[msg.user];
                const msgIsOwner = msg.user.toLowerCase() === 'im.phil_real';
                const display = msg.displayName || msg.user;
                const nameClass = msgIsOwner ? 'owner' : '';
                
                let replyHtml = msg.replyTo ? '<div class="reply-banner" style="display:block;margin:0 0 8px 0"><span>Replying to <strong>' + msg.replyTo.user + '</strong></span></div>' : '';
                let content = msg.type === 'image' ? '<img src="' + msg.text + '" class="message-img">' : processMentions(msg.text);
                if (isDeleted) return;
                
                const avatarHtml = msg.avatar ? '<img src="' + msg.avatar + '">' : msg.user.charAt(0).toUpperCase();
                
                div.innerHTML = '<div class="message-avatar" onclick="showUserProfile(\'' + msg.user + '\')">' + avatarHtml + '</div><div class="message-content"><div class="message-header"><span class="message-username ' + nameClass + '" onclick="showUserProfile(\'' + msg.user + '\')">' + display + (msgIsOwner ? '<span class="owner-tag-msg">Owner</span>' : '') + (msg.user !== display ? '<span class="display-name">@' + msg.user + '</span>' : '') + (isVerified ? '<span class="verified-icon">✓</span>' : '') + '</span><span class="message-time">' + time + '</span><span class="message-id" onclick="copyMessageId(\'' + msg.id + '\')">ID</span></div>' + replyHtml + '<div class="message-text">' + content + '</div></div><div class="message-actions"><button class="message-action-btn" onclick="replyToMessage(\'' + msg.id + '\',\'' + msg.user + '\',\'' + msg.text.substring(0,30).replace(/\'/g,"\\'") + '\')">↩️</button>' + (isOwner ? '<button class="message-action-btn" onclick="deleteAnyMessage(\'' + msg.id + '\')">🗑️</button>' : '<button class="message-action-btn" onclick="deleteMessage(\'' + msg.id + '\')">🗑️</button>') + '</div>';
                document.getElementById('messages').appendChild(div);
            });
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }
        
        function showUserProfile(user) {
            const isVerified = verifiedUsers[user];
            const userIsOwner = user.toLowerCase() === 'im.phil_real';
            document.getElementById('profileAvatarText').textContent = user.charAt(0).toUpperCase();
            document.getElementById('profileName').innerHTML = user + (isVerified ? ' <span class="verified-icon">✓</span>' : '') + (userIsOwner ? ' <span class="owner-tag">Main Developer & Owner</span>' : '');
            document.getElementById('profileName').className = 'profile-name' + (userIsOwner ? ' owner' : '');
            document.getElementById('profileUsername').textContent = '@' + user;
            document.getElementById('profileId').textContent = 'ID: click to copy';
            document.getElementById('profileOwnerTag').style.display = userIsOwner ? 'inline' : 'none';
            showModal('profileModal');
        }
        
        function copyMessageId(id) { navigator.clipboard.writeText(id); alert('Message ID copied: ' + id); }
        function replyToMessage(id, user, text) { replyingTo = { id, user, text: text.substring(0, 100) }; document.getElementById('replyBanner').style.display = 'flex'; document.getElementById('replyToUser').textContent = user; document.getElementById('msgInput').focus(); }
        function cancelReply() { replyingTo = null; document.getElementById('replyBanner').style.display = 'none'; }
        function deleteMessage(id) { if (!deletedMessages.includes(id)) { deletedMessages.push(id); saveMessages(); renderMessages(); } }
        
        function deleteAnyMessage(id) {
            if (!isOwner) return;
            if (!deletedMessages.includes(id)) {
                deletedMessages.push(id);
                saveMessages();
                renderMessages();
                alert('Message deleted!');
            }
        }
        
        function sendMessage() {
            const text = document.getElementById('msgInput').value.trim();
            if (!text) return;
            const key = currentDM ? 'dm_' + currentDM : currentServer + '_' + currentChannel;
            if (!messages[key]) messages[key] = [];
            const msg = {
                id: 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
                userId: userId,
                user: username,
                displayName: displayName,
                password: userPassword,
                avatar: userAvatar,
                text: text,
                type: 'text',
                time: new Date().toISOString(),
                replyTo: replyingTo
            };
            messages[key].push(msg);
            saveMessages();
            renderMessages();
            cancelReply();
            document.getElementById('msgInput').value = '';
            saveToServer(msg);
            if (client && client.isConnected()) { client.send('discord/' + roomName, JSON.stringify({...msg, target: currentDM, server: currentServer, channel: currentChannel}), 0, false); }
        }
        
        function sendImage(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const key = currentDM ? 'dm_' + currentDM : currentServer + '_' + currentChannel;
                if (!messages[key]) messages[key] = [];
                const msg = { id: 'msg_' + Date.now(), userId: userId, user: username, displayName: displayName, avatar: userAvatar, password: userPassword, text: e.target.result, type: 'image', time: new Date().toISOString() };
                messages[key].push(msg);
                saveMessages();
                renderMessages();
                if (client && client.isConnected()) client.send('discord/' + roomName, JSON.stringify({...msg, target: currentDM, server: currentServer, channel: currentChannel}), 0, false);
            };
            reader.readAsDataURL(file);
        }
        
        function setTheme(theme) {
            const themes = { 
                'dark': {bg:'#313338',bg2:'#2b2d31',bg3:'#1e1f22',text:'#dbdee1',muted:'#949ba4'}, 
                'light': {bg:'#f2f3f5',bg2:'#f2f3f5',bg3:'#e3e5e8',text:'#060607',muted:'#4e5058'}, 
                'sunset': {bg:'#3d2e2e',bg2:'#2d2323',bg3:'#1f1818',text:'#e4d4d4',muted:'#a89595'}, 
                'ocean': {bg:'#1e3a5f',bg2:'#162d4d',bg3:'#0f1f33',text:'#d4e5f7',muted:'#8ba4c7'}, 
                'midnight': {bg:'#1a1a2e',bg2:'#16213e',bg3:'#0f0f1a',text:'#e8e8e8',muted:'#8b8b9e'},
                'wine': {bg:'#2d1b1b',bg2:'#1f1414',bg3:'#150d0d',text:'#f0e0e0',muted:'#9a8585'},
                'forest': {bg:'#1a2f1a',bg2:'#142314',bg3:'#0d180d',text:'#e0f0e0',muted:'#7a9a7a'},
                'purple': {bg:'#2b1a4e',bg2:'#1e1238',bg3:'#130b25',text:'#e8e0f0',muted:'#9a85ba'}
            };
            const t = themes[theme];
            document.documentElement.style.setProperty('--bg-primary', t.bg);
            document.documentElement.style.setProperty('--bg-secondary', t.bg2);
            document.documentElement.style.setProperty('--bg-tertiary', t.bg3);
            document.documentElement.style.setProperty('--text-normal', t.text);
            document.documentElement.style.setProperty('--text-muted', t.muted);
            localStorage.setItem('theme', theme);
        }
        
        function showModal(id) { document.getElementById(id).classList.add('show'); }
        function hideModal(id) { document.getElementById(id).classList.remove('show'); }
        function saveUsername() { 
            const name = document.getElementById('usernameInput').value.trim(); 
            const pass = document.getElementById('newPasswordInput').value;
            const confirm = document.getElementById('newConfirmPasswordInput').value;
            
            if (!name) { alert('Please enter a username!'); return; }
            if (pass.length < 8) { alert('Password must be at least 8 characters!'); return; }
            if (pass !== confirm) { alert('Passwords do not match!'); return; }
            
            username = name; 
            userPassword = pass;
            verifiedUsers[username] = pass;
            localStorage.setItem('username', username);
            localStorage.setItem('userPassword', pass);
            saveMessages();
            checkOwner(); 
            loadUsername(); 
            hideModal('usernameModal'); 
            alert('Account created!');
        }
        function joinRoom() { const room = document.getElementById('roomInput').value.trim().toLowerCase().replace(/[^a-z0-9]/g, ''); if (room) { roomName = room; localStorage.setItem('room', roomName); connectToRoom(room); hideModal('roomModal'); } }
        function createDM() { const user = document.getElementById('newDmInput').value.trim(); const pass = document.getElementById('newDmPassword').value; if (userPassword && pass !== userPassword) { alert('Incorrect password!'); return; } if (user) { if (!friends.includes(user)) friends.push(user); loadFriends(); saveMessages(); openDM(user); hideModal('newDmModal'); } }
        function createServer() { const name = document.getElementById('serverNameInput').value.trim(); if (name) { serverCount++; servers[serverCount] = {name: name, icon: '🎮', channels: [{name:'general',type:'text'},{name:'Voice',type:'voice'}], owner: username}; saveMessages(); selectServer(serverCount.toString()); hideModal('createServerModal'); } }
        function createGroup() { const name = document.getElementById('groupNameInput').value.trim(); const membersInput = document.getElementById('groupMembersInput').value.trim(); if (name) { groups.push({name: name, members: membersInput ? membersInput.split(',') : []}); saveMessages(); loadFriends(); openGroup(name); hideModal('createGroupModal'); } }
        function addFriend() { const name = document.getElementById('friendNameInput').value.trim(); if (name && !friends.includes(name)) { friendRequests.push(name); saveMessages(); loadFriendRequests(); } hideModal('addFriendModal'); }
        function createChannel() { const name = document.getElementById('channelNameInput').value.trim(); if (name) { servers[currentServer].channels.push({name,type:'text'}); saveMessages(); loadChannels(); hideModal('createChannelModal'); } }
        function toggleSettings() { document.getElementById('settingsMenu').classList.toggle('show'); }
        function hideSettings() { document.getElementById('settingsMenu').classList.remove('show'); }
        function acceptFriend(name, index) { if (!friends.includes(name)) friends.push(name); friendRequests.splice(index, 1); saveMessages(); loadFriends(); loadFriendRequests(); }
        function declineFriend(name, index) { friendRequests.splice(index, 1); saveMessages(); loadFriendRequests(); }
        function startCall() { if (currentDM) { alert('Starting call with ' + currentDM); } else { alert('Start a DM first'); } }
        function startVideoCall() { if (currentDM) { alert('Starting video call with ' + currentDM); } else { alert('Start a DM first'); } }
        
        const EMOJIS = ['😀','😂','😊','😍','🤔','😢','😮','😎','😡','😭','😴','🤯','🤡','💀','👻','💪','👍','👎','❤️','🔥','⭐','✨','🎉','🎊','👋','🙏','💯','✅','❌','💡','🔔','🎵','🎮','🏆','💻','📱','📸','🌈','🌙','☀️','🌊','🍕','🍔','🍟','🎂','🍪','☕','🍺','🍻','🥳','🤓','🧐','🤠','👽','👾','🎃','🦄','🐱','🐶','🦁','🐻','🐼','🐨','🐯','🐝','🦋','🐢','🐙','🦀','🐠','🌸','🌺','🌻','🌹','🍀','🌵','🎄','🎋','🌴'];
        
        function showEmojiModal() {
            const grid = document.getElementById('emojiGrid');
            grid.innerHTML = EMOJIS.map(e => '<span style="font-size:24px;cursor:pointer;padding:4px" onclick="addEmoji(\'' + e + '\')">' + e + '</span>').join('');
            showModal('emojiModal');
        }
        
        function addEmoji(emoji) {
            const inputEl = document.getElementById('msgInput');
            inputEl.value += emoji;
            inputEl.focus();
            hideModal('emojiModal');
        }
        
        function showGifModal() { showModal('gifModal'); searchGifs(); }
        
        function searchGifs() {
            const results = document.getElementById('gifResults');
            const gifs = [
                {url: 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif', title: 'Funny'},
                {url: 'https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif', title: 'Laughing'},
                {url: 'https://media.giphy.com/media/l0MYGb1LuZ3n7dRnO/giphy.gif', title: 'Happy'},
                {url: 'https://media.giphy.com/media/l41YtZOb9EUABnuqA/giphy.gif', title: 'Dance'},
                {url: 'https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif', title: 'Yes'},
                {url: 'https://media.giphy.com/media/g9582DNuQppxC/giphy.gif', title: 'Love'},
                {url: 'https://media.giphy.com/media/l41JJi7y8J6lffalu/giphy.gif', title: 'Cat'},
                {url: 'https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif', title: 'Dog'},
                {url: 'https://media.giphy.com/media/l0Iyl55kTeh71nTXy/giphy.gif', title: 'Wow'}
            ];
            results.innerHTML = gifs.map(g => '<img src="' + g.url + '" style="width:100%;border-radius:8px;cursor:pointer" onclick="sendGif(\'' + g.url + '\')" title="' + g.title + '">').join('');
        }
        
        function sendGif(url) {
            const key = currentDM ? 'dm_' + currentDM : currentServer + '_' + currentChannel;
            if (!messages[key]) messages[key] = [];
            const msg = { id: 'msg_' + Date.now(), userId: userId, user: username, displayName: displayName, avatar: userAvatar, text: url, type: 'gif', time: new Date().toISOString() };
            messages[key].push(msg);
            saveMessages();
            renderMessages();
            hideModal('gifModal');
        }
        
        const msgInput = document.getElementById('msgInput');
        const autocomplete = document.getElementById('autocomplete');
        msgInput.addEventListener('input', function() {
            const text = this.value;
            const cursorPos = this.selectionStart;
            const lastAt = text.lastIndexOf('@', cursorPos - 1);
            if (lastAt !== -1) {
                const search = text.substring(lastAt + 1, cursorPos).toLowerCase();
                if (search.length > 0) {
                    const matches = friends.filter(f => f.toLowerCase().startsWith(search));
                    if (matches.length > 0) {
                        autocomplete.innerHTML = matches.map(f => '<div class="autocomplete-item" onclick="insertMention(\'' + f + '\')">@' + f + '</div>').join('');
                        autocomplete.style.left = '16px';
                        autocomplete.style.width = (this.offsetWidth - 32) + 'px';
                        autocomplete.classList.add('show');
                        return;
                    }
                }
            }
            autocomplete.classList.remove('show');
        });
        
        function insertMention(name) { const text = msgInput.value; const cursorPos = msgInput.selectionStart; const lastAt = text.lastIndexOf('@', cursorPos - 1); msgInput.value = text.substring(0, lastAt) + '@' + name + ' ' + text.substring(cursorPos); autocomplete.classList.remove('show'); msgInput.focus(); }
        
        document.getElementById('msgInput').onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
        document.getElementById('fileInput').onchange = (e) => { if (e.target.files[0]) sendImage(e.target.files[0]); e.target.value = ''; };
        document.onclick = (e) => { if (!e.target.closest('.settings-dropdown')) hideSettings(); autocomplete.classList.remove('show'); };
        document.querySelectorAll('.modal').forEach(m => m.onclick = (e) => { if (e.target === m) m.classList.remove('show'); });
        
        function connectToRoom(room) {
            client = new Paho.MQTT.Client('broker.hivemq.com', 8000, 'client_' + Math.random());
            client.onConnectionLost = () => {};
            client.onMessageArrived = (message) => {
                try {
                    const msg = JSON.parse(message.payloadString);
                    const isForCurrentChannel = currentDM ? msg.target === currentDM : msg.server === currentServer && msg.channel === currentChannel;
                    if (isForCurrentChannel && msg.user !== (username || 'User')) {
                        const key = msg.target ? 'dm_' + msg.target : msg.server + '_' + msg.channel;
                        if (!messages[key]) messages[key] = [];
                        const exists = messages[key].some(m => m.time === msg.time && m.user === msg.user);
                        if (!exists) {
                            if (msg.password) verifiedUsers[msg.user] = msg.password;
                            messages[key].push(msg);
                            saveMessages();
                            renderMessages();
                        }
                    }
                } catch(e) {}
            };
            client.connect({ onSuccess: () => { client.subscribe('discord/' + room, 0); }, useSSL: false });
        }
        
        if (localStorage.getItem('theme')) { setTheme(localStorage.getItem('theme')); }
        init();
        
        let isDev = false;
        let devHash = localStorage.getItem('devHash') || '';
        
        async function checkDevAuth() {
            const user = document.getElementById('devUsername').value;
            const pass = document.getElementById('devPassword').value;
            
            try {
                const response = await fetch(serverUrl + '/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', 'Authorization': API_KEY},
                    body: JSON.stringify({user: user, pass: pass})
                });
                const data = await response.json();
                
                if (data.success) {
                    isDev = true;
                    devHash = data.hash;
                    localStorage.setItem('devHash', devHash);
                    document.getElementById('devPanel').classList.add('show');
                    hideModal('devModal');
                    alert('Developer mode activated!');
                } else {
                    alert('Invalid credentials');
                }
            } catch(e) {
                alert('Auth failed: ' + e.message);
            }
        }
        
        function devDeleteAnyMessage() {
            const id = prompt('Enter message ID to delete:');
            if (id) { deleteAnyMessage(id); }
        }
        
        function devClearMessages() {
            if (confirm('Clear all messages?')) {
                messages = {};
                deletedMessages = [];
                saveMessages();
                renderMessages();
            }
        }
        
        function exitDevMode() {
            isDev = false;
            localStorage.removeItem('devHash');
            document.getElementById('devPanel').classList.remove('show');
        }
    </script>
</body>
</html>'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
    f.write(HTML_CONTENT)
    temp_file = f.name

webbrowser.open('file://' + temp_file)
