INSERT INTO preferences (userid, category, name, value)
SELECT id, 'theme', '', '{"type":"custom","sidebarBg":"#3F0E40","sidebarText":"#FFFFFF","sidebarHeaderBg":"#350d36","sidebarHeaderTextColor":"#FFFFFF","sidebarUnreadText":"#FFFFFF","sidebarTextHoverBg":"#350d36","sidebarTextActiveBorder":"#1164A3","sidebarTextActiveColor":"#FFFFFF","onlineIndicator":"#2BAC76","awayIndicator":"#E8912D","dndIndicator":"#E01E5A","mentionBg":"#CD2553","mentionColor":"#FFFFFF","centerChannelBg":"#FFFFFF","centerChannelColor":"#1D1C1D","newMessageSeparator":"#F26175","linkColor":"#1264A3","buttonBg":"#007A5A","buttonColor":"#FFFFFF","errorTextColor":"#E01E5A","mentionHighlightBg":"#FCF3CF","mentionHighlightLink":"#1264A3","codeTheme":"github"}'
FROM users WHERE username = 'admin'
ON CONFLICT (userid, category, name) DO UPDATE SET value = EXCLUDED.value;

INSERT INTO preferences (userid, category, name, value)
SELECT u.id, 'theme', t.id, '{"type":"custom","sidebarBg":"#3F0E40","sidebarText":"#FFFFFF","sidebarHeaderBg":"#350d36","sidebarHeaderTextColor":"#FFFFFF","sidebarUnreadText":"#FFFFFF","sidebarTextHoverBg":"#350d36","sidebarTextActiveBorder":"#1164A3","sidebarTextActiveColor":"#FFFFFF","onlineIndicator":"#2BAC76","awayIndicator":"#E8912D","dndIndicator":"#E01E5A","mentionBg":"#CD2553","mentionColor":"#FFFFFF","centerChannelBg":"#FFFFFF","centerChannelColor":"#1D1C1D","newMessageSeparator":"#F26175","linkColor":"#1264A3","buttonBg":"#007A5A","buttonColor":"#FFFFFF","errorTextColor":"#E01E5A","mentionHighlightBg":"#FCF3CF","mentionHighlightLink":"#1264A3","codeTheme":"github"}'
FROM users u CROSS JOIN teams t WHERE u.username = 'admin'
ON CONFLICT (userid, category, name) DO UPDATE SET value = EXCLUDED.value;
