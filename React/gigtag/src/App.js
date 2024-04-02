import { SpotifyAuth, Scopes } from 'react-spotify-auth'
import 'react-spotify-auth/dist/index.css' // if using the included styles
import React from 'react'
import { useCallback } from 'react'
import Cookies from 'js-cookie'
import { SpotifyInfo, SpotifyUserInfo } from './components/SpotifyInfo'
import './App.css';
import { Artists } from './components/Artists'
import { TargettedEvents } from './components/TargettedEvents'
import { useTelegramAuthResponse } from './components/TelegramAuth'
import BugReportButton from './components/BugReport'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: <TargettedEvents />
  },
  {
    path: "/artists",
    element: <Artists name='Artists' />
  },
  {
    path: "/playlists",
    element: <SpotifyInfo />
  }
]);

const App = () => {
  const [token, setToken] = React.useState(Cookies.get("spotifyAuthToken"))
  const [invalidToken, setInvalidToken] = React.useState(false);
  useTelegramAuthResponse();

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
            <RouterProvider router={router} />
          </SpotifyUserInfo>
        </div>
      ) : (
        // Display the login page
        <div className='centered-container'>
          <div className='d-grid'>
            <h1 className='spotify-font mb-5'><b>GigTag</b></h1>
            <h4 className='text-muted spotify-font-normal mb-5 text-uppercase'>Find local gigs for the bands <i>you</i> listen to</h4>
            <SpotifyAuth
              redirectUri={process.env.REACT_APP_REDIRECT_URI ?? 'http://localhost:3000'}
              clientID={process.env.REACT_APP_CLIENT_ID}
              scopes={[Scopes.userReadPrivate, Scopes.userReadEmail, Scopes.playlistReadPrivate, Scopes.playlistReadCollaborative, Scopes.userLibraryRead]}
              onAccessToken={(token) => {setToken(token); resetInvalid(false);}}
            />
          </div>
        </div>
      )}
      <BugReportButton />
    </div>
  )
}
export default App