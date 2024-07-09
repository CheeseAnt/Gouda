import { useContext, useEffect, useRef, useState } from "react";
import { Loader } from "./Loader";
import Event from "./Event";
import { EventContext } from "./EventContext";

const useNearBottom = () => {
    const [isNearBottom, setIsNearBottom] = useState(false);
    const previous = useRef(false);
    const [trigger, setTrigger] = useState(false);

    const handleScroll = (event) => {
        const { scrollHeight } = document.body;
        const { height } = window.screen;
        const { scrollY } = window;
        const threshold = height; // Adjust threshold value as needed (in pixels)

        const isCloseToBottom = scrollY >= (scrollHeight-height) - threshold;
        setIsNearBottom(isCloseToBottom);
    };

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);

        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    useEffect(() => {
        if (isNearBottom && !previous.current) {
            previous.current = true;
            setTrigger(true);
        }
        else if (!isNearBottom && previous.current) {
            previous.current = false;
            setTrigger(false);
        }
    }, [isNearBottom]);

    return {trigger};
}

const TargettedEvents = () => {
    const [ loadingMore, setLoadingMore ] = useState(true);
    const [ limit, setLimit ] = useState(50)
    const { trigger } = useNearBottom();

    const { displayedEvents, loading } = useContext(EventContext);

    useEffect(() => {
        if(!trigger) {
            return;
        }

        setLimit(previous => {
            if (previous >= displayedEvents.length) {
                setLoadingMore(false);

                return previous
            };

            setLoadingMore(true);
            return Math.min(previous + 10, displayedEvents.length)
        });
    }, [trigger, displayedEvents.length])

    return <div>
            {
            loading ? <Loader title="Loading your events, this shouldn't take too long!"/> :
            <div className='container'>
                <div className="container">
                    {displayedEvents.slice(0, limit).map((event, idx) => {
                        return <Event key={idx} eventData={event} />
                    })}
                    {displayedEvents.length === 0 ? <h3>No events found, have you enabled any <a href="/artists">artists</a> or <a href="/playlists">playlists</a>?</h3> : null}
                    {loadingMore ? <Loader /> : null}
                </div>
            </div>
            }
    </div>
}

export {TargettedEvents};
