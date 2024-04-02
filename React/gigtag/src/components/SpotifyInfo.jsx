import { useCallback, useEffect, useState } from 'react';
import { getUserInfo, refreshUserPlaylists, getUserPlaylists, togglePlaylist } from '../api'
import { Loader } from './Loader';
import { Navbar, Container, Nav, Dropdown, DropdownItem, Image } from 'react-bootstrap';
import { Logout, Settings } from '@mui/icons-material';
import UserSettings from './UserSettings';
import "./SpotifyInfo.css"

const UserDropdown = ({ userInfo, showSettings, logOut }) => {
    return (
      <Dropdown as="div" style={{userSelect: 'none'}}>
        <Dropdown.Toggle as="div" className="d-flex align-items-center" >
            <Image className="me-1 rounded-circle thumb-photo" src={userInfo.photo_url} alt="Profile" />
            <h3 className="fw-bold mx-2">{userInfo.name}</h3>
        </Dropdown.Toggle>
        <Dropdown.Menu>
            <div className='d-grid mx-2'>
                <span className='text-muted'>Playlists: {userInfo.playlists}</span>
                <span className='text-muted'>Artists: {userInfo.artists}</span>
            </div>
            <DropdownItem onClick={showSettings}>
                Settings <Settings />
            </DropdownItem>
            <DropdownItem onClick={logOut}>
                Log Out <Logout />
            </DropdownItem>
        </Dropdown.Menu>
      </Dropdown>
    );
  };

const SpotifyUserInfo = ( {setInvalid, children} ) => {
    const [userInfo, setUserInfo] = useState({});

    if(!(children instanceof Array)) {
        children = [children];
    }

    const getUser = useCallback(async () => {
        const res = await getUserInfo();
        if(!res.ok) {
            setInvalid(true);
            return;
        }

        const json = await res.json();

        setUserInfo(json);
    }, [setInvalid, setUserInfo]);

    useEffect(() => {
        getUser();
    }, [getUser]);

    const logOut = () => {
        setInvalid(true);
    };

    const [showS, setShowS] = useState(false);
    const showSettings = () => {
        setShowS(true);
    };

    return <div className='d-grid' style={{justifyItems: 'center'}}>
        <UserSettings show={showS} setShow={setShowS} user={userInfo} />
        <Navbar expand="lg" className="navbar-body w-100" data-bs-theme="dark">
            <Container>
                <Navbar.Brand className='spotify-font' href="#home">GigTag</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link href="/">Home</Nav.Link>
                        <Nav.Link href="/playlists">Playlists</Nav.Link>
                        <Nav.Link href="/artists">Artists</Nav.Link>
                    </Nav>
                </Navbar.Collapse>
                <Navbar.Text>
                </Navbar.Text>
                <UserDropdown userInfo={userInfo} showSettings={showSettings} logOut={logOut} />
            </Container>
        </Navbar>
        <div>
            {children}
        </div>
    </div>
}

const SpotifyPlaylists = () => {
    const [ playlists, setPlaylists ] = useState({});
    const [loading, setLoading] = useState(false);

    const refreshPlaylists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);

        const res = await refreshUserPlaylists();
        if(!res.ok) {
            console.log("Error loading playlists: ", res)
            return;
        }
        const json = await res.json();

        setPlaylists(json);

        setLoading(false);
    }, [loading, setLoading, setPlaylists]);

    const getPlaylists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);

        const res = await getUserPlaylists();
        if(!res.ok) {
            console.log("Error loading playlists: ", res)
            setLoading(false);
            return;
        }
        const json = await res.json();

        setPlaylists(json);
        setLoading(false);

        return Object.keys(json).length;
    }, [loading, setLoading, setPlaylists]);

    useEffect(() => {
        if(Object.keys(playlists).length) {
            return;
        }

        getPlaylists().then((res) => {
            if (!res) {
                refreshPlaylists();
            }
        })
    }, [getPlaylists, refreshPlaylists, playlists]);

    const togglePl = useCallback((playlist) => {
        togglePlaylist(playlist.id, !playlist.enabled);
        setPlaylists((previous) => ({
            ...previous,
            [playlist.id]: {
                ...previous[playlist.id],
                enabled: !previous[playlist.id].enabled,
            },
        }));
    }, [setPlaylists]);

    return <div>
        {
            loading ? <Loader /> :
            <div className='container'>
                <button className='btn gg-cream px-10 w-100 mt-3' onClick={refreshPlaylists}>Refresh from Spotify</button>
                <h4 className="text-muted">Total Playlists: {Object.keys(playlists).length}</h4>
                {Object.values(playlists).map(playlist => {
                    return <div key={playlist.id} className='playlist d-flex'>
                        <img className='me-3' alt='Playlist' style={{width: "64px"}} src={playlist.image_url} />
                        <div className='d-flex w-100' style={{justifyContent: 'space-between'}}>
                            <div>
                                <h1 className='fw-bold mx-3'>{playlist.name}</h1>
                                <h3 className='mx-3 text-muted'>{playlist.last_updated}</h3>
                                <div className='d-flex'>
                                    <h3 className='mx-3 text-muted'>Tracks: {playlist.track_count}</h3>
                                    <h3 className='mx-3 text-muted'>{playlist.public ? 'Public' : 'Private'}</h3>
                                    <h3 className='mx-3 text-muted'>{playlist.owner}</h3>
                                </div>
                            </div>
                            <button className='btn gg-cream m-3 px-4' style={{fontSize: 'xxx-large'}} data-mdb-toggle="button" onClick={() => togglePl(playlist)}>
                                {playlist.enabled ? '☑' : '☐'}
                            </button>
                        </div>
                    </div>
                })}
            </div>
        }
    </div>
}

const SpotifyInfo = ({setInvalid}) => {
    return (
        <div className='container'>
            <SpotifyPlaylists />
        </div>
    )
}

export { SpotifyInfo, SpotifyUserInfo }
