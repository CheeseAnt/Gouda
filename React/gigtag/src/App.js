import { SpotifyAuth, Scopes } from 'react-spotify-auth'
import 'react-spotify-auth/dist/index.css' // if using the included styles
import React from 'react'
import { useCallback } from 'react'
import Cookies from 'js-cookie'
import { SpotifyInfo, SpotifyUserInfo } from './components/SpotifyInfo'
import './App.css';
import { Artists } from './components/Artists'

const App = () => {
  const [token, setToken] = React.useState(Cookies.get("spotifyAuthToken"))
  const [invalidToken, setInvalidToken] = React.useState(false);

  const resetInvalid = useCallback(
    (invalid) => {
    setInvalidToken(invalid);
    window.location.hash = "";

    if(invalid) {
      Cookies.remove("spotifyAuthToken");
      localStorage.clear("spotifyAuthToken");
    }
  }, [setInvalidToken]);
  
  return (
    <div className='app'>
      {!invalidToken && token ? (
        <div>
          <SpotifyUserInfo setInvalid={resetInvalid}>
            <SpotifyInfo name='Playlists' />
            <Artists name='Artists' />
          </SpotifyUserInfo>
        </div>
      ) : (
        // Display the login page
        <div className='centered-container'>
          <div>
            <h1 className='spotify-font'><b>GigTag</b></h1>
            <SpotifyAuth
              redirectUri={process.env.REACT_APP_REDIRECT_URI ?? 'http://localhost:3000'}
              clientID={process.env.REACT_APP_CLIENT_ID}
              scopes={[Scopes.userReadPrivate, Scopes.userReadEmail, Scopes.playlistReadPrivate, Scopes.playlistReadCollaborative, Scopes.userLibraryRead]}
              onAccessToken={(token) => {setToken(token); resetInvalid(false);}}
            />
          </div>
        </div>
      )}
    </div>
  )
}
export default App