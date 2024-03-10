import { SpotifyAuth, Scopes } from 'react-spotify-auth'
import 'react-spotify-auth/dist/index.css' // if using the included styles
import React from 'react'
import { SpotifyApiContext } from 'react-spotify-api'
import Cookies from 'js-cookie'
import { SpotifyInfo } from './components/SpotifyInfo'

const App = () => {
  const [token, setToken] = React.useState(Cookies.get("spotifyAuthToken"))
  return (
    <div className='app'>
      {token ? (
        <SpotifyApiContext.Provider value={token}>
          <SpotifyInfo />
          <p>You are authorized with token: {token}</p>
        </SpotifyApiContext.Provider>
      ) : (
        // Display the login page
        <SpotifyAuth
          redirectUri={process.env.REACT_APP_REDIRECT_URI ?? 'http://localhost:3000'}
          clientID={process.env.REACT_APP_CLIENT_ID}
          scopes={[Scopes.userReadPrivate, Scopes.userReadEmail, Scopes.playlistReadPrivate, Scopes.playlistReadCollaborative]}
          onAccessToken={(token) => setToken(token)}
        />
      )}
    </div>
  )
}
export default App