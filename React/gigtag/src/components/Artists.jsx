import { useCallback, useEffect, useState } from "react";
import { getuserArtists, refreshUserArtists } from "../api";
import { Loader } from "./Loader";
import { toggleArtist } from "../api";
import ArtistEvents from "./ArtistEvents";

const useArtists = () => {
    const [artists, setArtists] = useState([]);
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);

    const getArtists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);
        const res = await getuserArtists();

        if(!res.ok) {
            setLoading(false);
            setDone(true);
            console.log("Failed to fetch user artists", res)
            return;
        }

        setArtists(await res.json());
        setLoading(false);
        setDone(true);
    }, [loading, setArtists, setLoading, setDone]);

    const refreshArtists = useCallback(async () => {
        if(loading) {
            return;
        }
        setLoading(true);
        const res = await refreshUserArtists();

        if(!res.ok) {
            setLoading(false);
            console.log("Failed to fetch user artists", res)
            return;
        }

        setArtists(await res.json());
        setLoading(false);
    }, [loading, setArtists, setLoading]);

    const toggleAr = useCallback(async (artist) => {
        toggleArtist(artist.name, !artist.enabled);
        setArtists((previous) => ({
            ...previous,
            [artist.name]: {
                ...previous[artist.name],
                enabled: !previous[artist.name].enabled,
            },
        }));
    }, [setArtists])

    useEffect(() => {
        if(Object.keys(artists).length || done) {
            return;
        }
        getArtists()
    }, [getArtists, artists, done]);

    return { artists, loading, refreshArtists, toggleAr };
}

const Artists = () => {
    const { artists, loading, refreshArtists, toggleAr } = useArtists();
    const [ sortedArtists, setSortedArtists ] = useState([]);
    const [ sortType, setSortType ] = useState('byTracks');

    useEffect(() => {
        const sorts = {
            byName: (artists) => { return Object.values(artists) },
            byTracks: (artists) => { return Object.values(artists).sort((a, b) => b.tracks-a.tracks) }
        };

        setSortedArtists(sorts[sortType](artists));
    }, [artists, sortType])

    const [show, setShow] = useState(false);
    const [artist, setArtist] = useState({});

    const displayArtistEvents = useCallback((artist) => {
        setArtist(artist);
        setShow(true);
    }, [setArtist, setShow]);

    return <div>
        <ArtistEvents artist={artist} show={show} setShow={setShow} />
        {
            loading ? <Loader /> :
            <div className='container'>
                <button className='btn btn-info px-10 w-100' onClick={refreshArtists}>Refresh from Spotify</button>
                <div className="d-flex">
                    <button className='btn btn-secondary m-1 w-50' onClick={() => setSortType('byName')}>Sort By Name</button>
                    <button className='btn btn-secondary m-1 w-50' onClick={() => setSortType('byTracks')}>Sort By Favourite</button>
                </div>
                <h4 className="text-muted">Total Artists: {Object.keys(artists).length}</h4>
                {sortedArtists.map(artist => {
                    return <div key={artist.name} onClick={() => displayArtistEvents(artist)} className='artist d-flex'>
                        <div className='d-flex w-100' style={{justifyContent: 'space-between'}}>
                            <div>
                                <h1 className='fw-bold mx-3'>{artist.name}</h1>
                                <div className="d-flex">
                                    <h3 className="mx-3 text-muted">Tracks: {artist.tracks}</h3>
                                    <h3 className='mx-3 text-muted'>{artist.last_updated}</h3>
                                </div>
                            </div>
                            <button className='btn btn-info m-3 px-4' style={{fontSize: 'xxx-large'}} data-mdb-toggle="button" onClick={(e) => {toggleAr(artist); e.stopPropagation()}}>
                                {artist.enabled ? '☑' : '☐'}
                            </button>
                        </div>
                    </div>
                })}
            </div>
        }
    </div>
}

export {Artists};
