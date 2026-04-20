
(function() {
    'use strict';

    /**
     * Initialize sidebar navigation on page load
     */
    document.addEventListener('DOMContentLoaded', function() {
        initializeSidebarNavigation();
        attachMenuToggleHandlers();
    });

    /**
     * Set active navigation state based on current URL
     */
    function initializeSidebarNavigation() {
        const currentPath = window.location.pathname;
        const sidebar = document.querySelector('.sidebar-nav');
        
        if (!sidebar) {
            console.warn('Sidebar navigation not found');
            return;
        }

        // Get all navigation links
        const allLinks = sidebar.querySelectorAll('a');
        const submenus = sidebar.querySelectorAll('.nav-content.collapse');
        
        // Step 1: Reset all states - close all submenus and remove active classes
        resetNavigationStates(allLinks, submenus);
        
        // Step 2: Find and activate the best-matching current page link
        activateCurrentPage(allLinks, currentPath);
    }

    /**
     * Reset all navigation states to default (collapsed/inactive)
     */
    function resetNavigationStates(links, submenus) {
        // Close all submenus
        submenus.forEach(function(submenu) {
            submenu.classList.remove('show');
        });
        
        // Remove active classes and add collapsed class to all links
        links.forEach(function(link) {
            link.classList.add('collapsed');
            link.classList.remove('active');
            
            // Reset aria-expanded for collapse toggles
            if (link.hasAttribute('data-bs-toggle')) {
                link.setAttribute('aria-expanded', 'false');
            }
        });
    }

    /**
     * Activate the single best-matching navigation item for the current page
     */
    function activateCurrentPage(links, currentPath) {
        // Normalize current path (remove trailing slash)
        currentPath = stripTrailingSlash(currentPath);

        let bestMatchLink = null;
        let bestScore = 0;

        links.forEach(function(link) {
            const itemHref = link.getAttribute('href');
            
            // Skip if no href or if it's a dropdown toggle (#)
            if (!itemHref || itemHref === '#') return;
            
            // Normalize the path for comparison
            const itemPath = normalizeUrl(itemHref);
            const normalizedItemPath = stripTrailingSlash(itemPath);

            // Get a numeric score for how well this link matches
            const score = getMatchScore(currentPath, normalizedItemPath);

            if (score > bestScore) {
                bestScore = score;
                bestMatchLink = link;
            }
        });

        // Only activate the single best match
        if (bestMatchLink) {
            activateLink(bestMatchLink);
        } else {
            console.log('No matching navigation item found for:', currentPath);
        }
    }

    /**
     * Normalize URL for comparison
     * - Remove protocol and domain if present
     */
    function normalizeUrl(url) {
        return url.replace(/^https?:\/\/[^\/]+/, '');
    }

    /**
     * Remove trailing slash from a path (except if it's just "/")
     */
    function stripTrailingSlash(path) {
        if (path.length > 1 && path.endsWith('/')) {
            return path.slice(0, -1);
        }
        return path;
    }

    /**
     * Compute a score for how well a nav item path matches the current path
     * Higher score = better match
     */
    function getMatchScore(currentPath, itemPath) {
        // Exact match: highest priority
        if (currentPath === itemPath) {
            // Add large constant so exact matches always beat prefix matches
            return itemPath.length + 1000;
        }

        // If the link path is a prefix of the current path
        // e.g. /students for /students/create
        if (itemPath !== '' && currentPath.startsWith(itemPath + '/')) {
            // Longer prefixes are better
            return itemPath.length;
        }

        // No match
        return 0;
    }

    /**
     * Activate a navigation link and expand its parent menu if needed
     */
    function activateLink(link) {

        // 1. Deselect all sibling links inside the same <ul>
        const parentList = link.closest('ul');
        if (parentList) {
            parentList.querySelectorAll('a').forEach(function(sibling) {
                sibling.classList.remove('active');
            });
        }

        // 2. Activate the clicked/current link
        link.classList.remove('collapsed');
        link.classList.add('active');

        // 3. Expand parent menu if this is inside a submenu
        const parentCollapse = link.closest('.nav-content.collapse');
        if (parentCollapse) {
            expandParentMenu(parentCollapse);
        }
    }

    /**
     * Expand the parent menu of a submenu item
     */
    function expandParentMenu(submenu) {
        // Add show class to the submenu
        submenu.classList.add('show');
        
        // Find the parent li element
        const parentLi = submenu.parentElement;
        
        if (parentLi) {
            // Find the toggle link in the parent li
            const toggleLink = parentLi.querySelector('a[data-bs-toggle="collapse"]');
            
            if (toggleLink) {
                // Remove collapsed class and update aria-expanded
                toggleLink.classList.remove('collapsed');
                toggleLink.setAttribute('aria-expanded', 'true');
            }
        }
    }

    /**
     * Attach click handlers to menu toggle links for accordion behavior
     */
    function attachMenuToggleHandlers() {
        const sidebar = document.querySelector('.sidebar-nav');
        
        if (!sidebar) return;
        
        // Get all top-level menu toggle links
        const toggleLinks = sidebar.querySelectorAll('.nav-item > a[data-bs-toggle="collapse"]');
        
        toggleLinks.forEach(function(toggleLink) {
            toggleLink.addEventListener('click', function() {
                handleMenuToggle(this);
            });
        });
    }

    /**
     * Handle menu toggle click to implement accordion behavior
     */
    function handleMenuToggle(toggleLink) {
        const targetId = toggleLink.getAttribute('data-bs-target');
        const targetSubmenu = document.querySelector(targetId);
        
        if (!targetSubmenu) return;
        
        // If this menu is being opened (not currently shown)
        if (!targetSubmenu.classList.contains('show')) {
            // Close all other open submenus at the same level
            closeOtherSubmenus(targetSubmenu);
        }
    }

    /**
     * Close all other submenus except the specified one
     */
    function closeOtherSubmenus(exceptSubmenu) {
        const sidebar = document.querySelector('.sidebar-nav');
        
        if (!sidebar) return;
        
        // Get all open submenus at the top level
        const openSubmenus = sidebar.querySelectorAll('.nav-item > .nav-content.collapse.show');
        
        openSubmenus.forEach(function(submenu) {
            if (submenu !== exceptSubmenu) {
                // Close the submenu
                submenu.classList.remove('show');
                
                // Update the parent toggle link
                const parentLi = submenu.parentElement;
                if (parentLi) {
                    const parentLink = parentLi.querySelector('a[data-bs-toggle="collapse"]');
                    if (parentLink) {
                        parentLink.classList.add('collapsed');
                        parentLink.setAttribute('aria-expanded', 'false');
                    }
                }
            }
        });
    }

    /**
     * Optional: Handle browser back/forward navigation
     */
    window.addEventListener('popstate', function() {
        initializeSidebarNavigation();
    });

})();
