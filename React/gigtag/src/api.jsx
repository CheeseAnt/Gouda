import Cookies from "js-cookie"

function getAuthToken() {
    const token = Cookies.get("spotifyAuthToken");
    return token;
}

async function makeRequest(endpoint, params, method) {
    return await fetch(
        (process.env.REACT_APP_API_HOST ?? "http://localhost:8000/") + endpoint,
        {
            body: params ? JSON.stringify(params) : undefined,
            method: method ?? (params ? 'POST' : 'GET'),
            headers: {
                "Authorization": "Bearer " + getAuthToken()
            }
        }
    )
}

async function getUserInfo() {
    return await makeRequest("user_info")
}

async function getUserPlaylists() {
    return await makeRequest("user_playlists")
}

async function refreshUserPlaylists() {
    return await makeRequest("refresh_playlists")
}

async function togglePlaylist(id, enable) {
    return await makeRequest("toggle_playlist", {id: id, enabled: enable})
}

async function toggleArtist(name, enable) {
    return await makeRequest("toggle_artist", {name: name, enabled: enable})
}

async function getuserArtists() {
    return await makeRequest("user_artists")
}

async function getArtistEvents(artist, refresh=false) {
    return await makeRequest("artist_events", {artist: artist, refresh: refresh})
}

async function getUserSettings() {
    return await makeRequest("user/settings")
}

async function updateUserCountries(countries) {
    return await makeRequest("update_user", {countries: countries})
}

async function updateUserNotification(notify) {
    return await makeRequest("update_user", {notify_for_gigs: notify})
}

async function updateUserTelegramID(id) {
    return await makeRequest("update_user", {telegramID: id})
}

async function submitBugReport(text) {
    return await makeRequest("bug_report", {text: text})
}

async function getUserCountryEnabledEvents() {
    return await makeRequest("user_events")
}

async function refreshUserArtists() {
    return await makeRequest("user_artists?fresh=1")
}

export { getUserInfo, getUserPlaylists, refreshUserPlaylists, togglePlaylist, getuserArtists, refreshUserArtists, toggleArtist, getArtistEvents, getUserSettings, updateUserCountries, getUserCountryEnabledEvents, updateUserTelegramID, submitBugReport, updateUserNotification }
