// Famly Feed Capture Script
// Run this in the browser console on app.famly.co to capture feed data

(function() {
    let capturedData = [];
    let isCapturing = false;
    
    console.log('🔧 Setting up network interceptors...');
    
    // Override XMLHttpRequest to capture feed API calls
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        const xhr = new originalXHR();
        const originalOpen = xhr.open;
        const originalSend = xhr.send;
        
        xhr.open = function(method, url, ...args) {
            this._url = url;
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        xhr.send = function(...args) {
            console.log('📡 XHR Send:', this._url);
            if (this._url && this._url.includes('/api/feed')) {
                console.log('🎯 Intercepting XHR feed API call:', this._url);
                const originalOnLoad = this.onload;
                this.onload = function() {
                    if (originalOnLoad) originalOnLoad.apply(this, arguments);
                    
                    if (this.status === 200 && isCapturing) {
                        try {
                            const data = JSON.parse(this.responseText);
                            if (data.feedItems && data.feedItems.length > 0) {
                                console.log(`✅ Captured ${data.feedItems.length} feed items from XHR: ${this._url}`);
                                capturedData.push({
                                    url: this._url,
                                    timestamp: new Date().toISOString(),
                                    data: data
                                });
                            }
                        } catch (e) {
                            console.error('❌ Error parsing XHR feed response:', e);
                        }
                    }
                };
            }
            return originalSend.apply(this, args);
        };
        
        return xhr;
    };
    
    // Override fetch to capture feed API calls (modern apps use fetch instead of XHR)
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        console.log('🌐 Fetch:', url);
        
        if (url && url.toString().includes('/api/feed')) {
            console.log('🎯 Intercepting fetch feed API call:', url);
            
            return originalFetch.apply(this, arguments).then(response => {
                if (response.ok && isCapturing) {
                    // Clone the response so we can read it without consuming the original
                    const clonedResponse = response.clone();
                    clonedResponse.json().then(data => {
                        if (data.feedItems && data.feedItems.length > 0) {
                            console.log(`✅ Captured ${data.feedItems.length} feed items from fetch: ${url}`);
                            capturedData.push({
                                url: url.toString(),
                                timestamp: new Date().toISOString(),
                                data: data
                            });
                        }
                    }).catch(e => {
                        console.error('❌ Error parsing fetch feed response:', e);
                    });
                }
                return response;
            });
        }
        
        return originalFetch.apply(this, arguments);
    };
    
    console.log('✅ Network interceptors installed');
    
    // Control functions
    window.famlyCapture = {
        start: function() {
            isCapturing = true;
            capturedData = [];
            console.log('🟢 Famly capture started. Scroll through your feed to capture data.');
            console.log('💡 Tip: Open Network tab in DevTools to see all requests');
            console.log('Use famlyCapture.stop() when done, then famlyCapture.download() to save.');
        },
        
        stop: function() {
            isCapturing = false;
            console.log(`🔴 Famly capture stopped. Captured ${capturedData.length} API responses.`);
        },
        
        status: function() {
            console.log(`📊 Status: ${isCapturing ? '🟢 Capturing' : '🔴 Stopped'}`);
            console.log(`📦 Captured responses: ${capturedData.length}`);
            
            const totalItems = capturedData.reduce((sum, response) => {
                return sum + (response.data.feedItems ? response.data.feedItems.length : 0);
            }, 0);
            console.log(`📸 Total feed items: ${totalItems}`);
            
            if (capturedData.length > 0) {
                console.log('🔗 Recent URLs captured:');
                capturedData.slice(-3).forEach(item => {
                    console.log(`  - ${item.url}`);
                });
            }
        },
        
        debug: function() {
            console.log('🔍 Debug info:');
            console.log('- Current URL:', window.location.href);
            console.log('- User agent:', navigator.userAgent);
            console.log('- Fetch override active:', window.fetch !== originalFetch);
            console.log('- XHR override active:', window.XMLHttpRequest !== originalXHR);
            
            // Test if we can see any network activity
            console.log('🧪 Testing network detection...');
            console.log('Try scrolling or refreshing the feed to see network requests');
        },
        
        download: function() {
            if (capturedData.length === 0) {
                console.log('No data captured yet. Use famlyCapture.start() first.');
                return;
            }
            
            // Merge all feed items
            const allFeedItems = [];
            capturedData.forEach(response => {
                if (response.data.feedItems) {
                    allFeedItems.push(...response.data.feedItems);
                }
            });
            
            // Remove duplicates based on feedItemId
            const uniqueItems = [];
            const seenIds = new Set();
            allFeedItems.forEach(item => {
                if (!seenIds.has(item.feedItemId)) {
                    seenIds.add(item.feedItemId);
                    uniqueItems.push(item);
                }
            });
            
            const exportData = {
                exportDate: new Date().toISOString(),
                totalItems: uniqueItems.length,
                feedItems: uniqueItems
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `famly_feed_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log(`📥 Downloaded ${uniqueItems.length} unique feed items to ${a.download}`);
        }
    };
    
    console.log('🚀 Famly Feed Capture loaded!');
    console.log('📋 Commands:');
    console.log('  famlyCapture.start() - Start capturing');
    console.log('  famlyCapture.stop()  - Stop capturing');
    console.log('  famlyCapture.status() - Check status');
    console.log('  famlyCapture.debug() - Debug network detection');
    console.log('  famlyCapture.download() - Download captured data');
    console.log('');
    console.log('💡 If you don\'t see network requests, try:');
    console.log('  1. Open DevTools Network tab');
    console.log('  2. Refresh the page');
    console.log('  3. Run famlyCapture.debug()');
})();
