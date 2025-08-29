// Famly Feed Capture Script
// Run this in the browser console on app.famly.co to capture feed data

(function() {
    let capturedData = [];
    let isCapturing = false;
    
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
            if (this._url && this._url.includes('/api/feed')) {
                const originalOnLoad = this.onload;
                this.onload = function() {
                    if (originalOnLoad) originalOnLoad.apply(this, arguments);
                    
                    if (this.status === 200 && isCapturing) {
                        try {
                            const data = JSON.parse(this.responseText);
                            if (data.feedItems && data.feedItems.length > 0) {
                                console.log(`Captured ${data.feedItems.length} feed items from: ${this._url}`);
                                capturedData.push({
                                    url: this._url,
                                    timestamp: new Date().toISOString(),
                                    data: data
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing feed response:', e);
                        }
                    }
                };
            }
            return originalSend.apply(this, args);
        };
        
        return xhr;
    };
    
    // Control functions
    window.famlyCapture = {
        start: function() {
            isCapturing = true;
            capturedData = [];
            console.log('🟢 Famly capture started. Scroll through your feed to capture data.');
            console.log('Use famlyCapture.stop() when done, then famlyCapture.download() to save.');
        },
        
        stop: function() {
            isCapturing = false;
            console.log(`🔴 Famly capture stopped. Captured ${capturedData.length} API responses.`);
        },
        
        status: function() {
            console.log(`Status: ${isCapturing ? 'Capturing' : 'Stopped'}`);
            console.log(`Captured responses: ${capturedData.length}`);
            
            const totalItems = capturedData.reduce((sum, response) => {
                return sum + (response.data.feedItems ? response.data.feedItems.length : 0);
            }, 0);
            console.log(`Total feed items: ${totalItems}`);
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
    
    console.log('Famly Feed Capture loaded!');
    console.log('Commands:');
    console.log('  famlyCapture.start() - Start capturing');
    console.log('  famlyCapture.stop()  - Stop capturing');
    console.log('  famlyCapture.status() - Check status');
    console.log('  famlyCapture.download() - Download captured data');
})();
