import React, { createContext, useContext, useEffect, useCallback, useState, useMemo } from 'react';
import { slide as Menu } from 'react-burger-menu';
import styles from './EventFilter.module.css'
import { FilterListOutlined } from '@mui/icons-material';
import { Button, Checkbox, Input, List, ListItem, ListItemButton, ListItemIcon, ListItemText, ListSubheader, Slider } from '@mui/material';
import { EventContext } from './EventContext';

const FilterContext = createContext({});

const useFilter = (filter) => {
  const { registerFilter, unregisterFilter } = useContext(FilterContext);

  useEffect(() => {
    registerFilter(filter);
    return () => {
      unregisterFilter(filter);
    };
  }, [filter, registerFilter, unregisterFilter]);
};

const FilterProvider = ({children, data, onFilterChange}) => {
  const [filters, setFilters] = useState([]);

  const registerFilter = useCallback((filter) => {
    setFilters((prevFilters) => [...prevFilters, filter]);
  }, []);

  const unregisterFilter = useCallback((filter) => {
    setFilters((prevFilters) => prevFilters.filter(f => f !== filter));
  }, []);

  const applyFilters = useCallback(() => {
    const filteredData = data.filter(dataPoint => {

      for (let index = 0; index < filters.length; index++) {
        const filter = filters[index];
        if(!filter(dataPoint)) {
          return false;
        }
      }
  
      return true;
    });

    onFilterChange(filteredData);
  }, [onFilterChange, data, filters]);

  const provided = {
    registerFilter,
    unregisterFilter,
    applyFilters,
  };

  return <FilterContext.Provider value={provided}>
    {children}
  </FilterContext.Provider>
}

const CheckFilter = ({filters, title, dataKey, condition}) => {
  const [checked, setChecked] = useState({});
  const [checksToDisplay, setChecksToDisplay] = useState([]);
  const filteredValues = useMemo(() => Object.keys(checked).filter(key => checked[key]), [checked]);

  const filter = useCallback((dataPoint) => {
    // default to true
    if(!filteredValues.length) {
      return true;
    }

    // filter by the condition otherwise
    const dataValue = dataPoint[dataKey];
    return (condition ?? (() => true))(dataValue, filteredValues);
  }, [filteredValues, dataKey, condition]);

  useFilter(filter);

  useEffect(() => {
    const c = filters.reduce((acc, filter) => {acc[filter] = false; return acc;}, {});
    setChecked(c);
    setChecksToDisplay(filters);
  }, [filters])

  const onChange = (key) => {
    setChecked((prev) => {prev[key] = !prev[key]; return {...prev}});
  }

  const onSearch = (event) => {
    const term = event.target.value?.toLowerCase();

    if(!term) {
      setChecksToDisplay(Object.keys(checked));
    }
    else {
      setChecksToDisplay(Object.keys(checked).filter(checkKey => checkKey.toLowerCase().includes(term)));
    }
  }

  return <div className={styles.filterSectionContainer}>
    <div className='d-flex align-items-center'>
      <ListSubheader className={styles.subtitle}>{title}</ListSubheader>
      <Input className={styles.filterSearch} placeholder={`Search for ${title}...`} onChange={onSearch}/>
    </div>
    <List className={styles.filterSection}>
      {checksToDisplay.map((key, idx) => {
        return <ListItem key={idx} className={styles.filterItem}>
        <ListItemButton className={styles.filterButton} onClick={() => onChange(key)} dense>
          <ListItemIcon className={styles.filterIcon}>
            <Checkbox
              edge="start"
              checked={checked[key]}
              disableRipple
            />
          </ListItemIcon>
          <ListItemText primary={key} />
        </ListItemButton>
      </ListItem>
      })}
    </List>
  </div>
}

const DateFilter = ({min, max, title, dataKey, condition}) => {
  const [dateRange, setDateRange] = useState([
    min,
    max,
  ]);

  const filter = useCallback((dataPoint) => {
    // default to true
    if(!dateRange) {
      return true;
    }

    // filter by the condition otherwise
    const dataValue = dataPoint[dataKey];
    return (condition ?? (() => true))(dataValue, dateRange);
  }, [dateRange, dataKey, condition]);

  useFilter(filter);

  const onChange = (_, newValue) => {
    setDateRange(newValue)
  };

  const valueLabelFormat = (value) => {
    return new Date(value).toDateString();
  };

  return <div className={styles.filterSectionContainer}>
    <ListSubheader className={styles.subtitle}>{title}</ListSubheader>
    <div className={styles.dateSliderContainer}>
      <Slider
        className={styles.dateFilter}
        getAriaLabel={() => title}
        value={dateRange}
        min={min}
        max={max}
        onChange={onChange}
        valueLabelDisplay="auto"
        valueLabelFormat={valueLabelFormat}
      />
    </div>
  </div>
}

const EventFilter = () => {
  // const [filters, setFilters] = useState({
  //   artist: '',
  //   venue: '',
  //   country: '',
  //   date: '',
  //   price: '',
  // });

  const { loading, events, setDisplayedEvents, displayedEvents } = useContext(EventContext);

  const artists = useMemo(() => {
    let artists = [];
    events.forEach(event => {
      event.artists?.split(",").forEach(artist => artists.push(artist))
    })
    artists = [...(new Set(artists))].sort();
    return artists;
  }, [events]);

  const venues = useMemo(() => {
    let venues = events.map(event=>event.venue);
    venues = [...(new Set(venues))].sort();
    return venues;
  }, [events]);

  const [minDate, maxDate] = useMemo(() => {
    let dates = events.map(event=>event.start_date.getTime()).filter(date=>date).sort()
    const minDate = dates[0];
    const maxDate = dates[dates.length-1];

    return [minDate, maxDate];
  }, [events]);

  if(loading || events.length===0) return null;

  return <div>
    <FilterProvider data={events} onFilterChange={setDisplayedEvents}>
      <Menu className={`${styles.sideBar}`}
      noOverlay={true} isOpen={true}
      burgerBarClassName={styles.burgerBar}
      burgerButtonClassName={styles.burgerButton}
      menuClassName={styles.burgerMenu}
      customBurgerIcon={<FilterListOutlined />}
      >
        <h4 className="text-muted">Events: {displayedEvents.length}</h4>
        <CheckFilter filters={artists} title='Artist' dataKey='artists' condition={
          (artists, filtered) => (new Set(filtered)).intersection(new Set(artists.split(","))).size
        }/>
        <CheckFilter filters={venues} title='Venue' dataKey='venue' condition={
          (venue, filtered) => filtered.includes(venue)
        }/>
        <DateFilter min={minDate} max={maxDate} title='Date' dataKey='start_date' condition={
          (start, minmax) => (minmax[0] <= start.getTime() && start.getTime() <= minmax[1])
        }/>
        <div className={styles.applyButtonContainer}>
          <FilterContext.Consumer>
            {ctx => <Button onClick={ctx.applyFilters} className={`gg-black ${styles.applyButton}`}>Apply</Button>}
          </FilterContext.Consumer>
        </div>
      </Menu>
    </FilterProvider>
  </div>
};

export default EventFilter;
