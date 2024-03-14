import React from 'react';
import { Box, Card, CardContent, CardMedia, Divider, Typography, Grid, Chip } from '@mui/material';
import { Container } from 'react-bootstrap';

const Event = ({ eventData }) => {
    const {
        event_details: {
        name,
        images,
        url,
        dates: { start },
        sales,
        classifications: [primaryClassification],
        priceRanges,
        _embedded: { venues: [venue] },
        },
    } = eventData;

    const formattedDate = new Date(start.dateTime).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });

    const genre = primaryClassification?.genre?.name || 'Rock';

    const priceDisplay = priceRanges
        ? `${priceRanges[0].currency} ${priceRanges[0].min} - ${priceRanges[0].max}`
        : 'Price TBA';

    const getBestImage = (images) => {
        let width = 0;
        let selimage = null;
        images.forEach((image) => {
            if(image.width > width) {
                width = image.width;
                selimage = image;
            }
        })
        return selimage.url;
    }

    const parseSale = (sale) => {
        const name = sale.name ?? 'Public';
        const date = new Date(sale.startDateTime);
        const start = date.toLocaleString('en-UK') ?? 'TBA';
        const started = date < (new Date());

        return {name, start, date, started}
    }

    const saleValues = [
        parseSale(sales['public']),
        ...(sales['presales'] ? sales['presales'].map((sale) => parseSale(sale)) : [])
    ];

    return (
        <a href={url} target='_blank' rel='noreferrer' style={{all: 'unset'}}>
        <Container className='my-2'>
        <Card className='event' sx={{ maxWidth: 600, margin: 'auto' }}>
            <CardMedia
            component="img"
            height="240"
            image={getBestImage(images)}
            alt={name}
            />
            <CardContent>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <div className='d-flex'>
                        <Typography variant="h5" component="div">
                            {name}
                        </Typography>
                        <Chip label={genre} color="primary" variant="contained" sx={{ mx: 1 }} />
                    </div>
                    </Grid>
                    <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                        Date:
                    </Typography>
                    <Typography variant="body1">{formattedDate}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                        Venue:
                    </Typography>
                    <Typography variant="body1">{venue.name}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                        Price:
                    </Typography>
                    <Typography variant="body1">{priceDisplay}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                        Sale Times:
                    </Typography>
                    {saleValues.map(sale => 
                        <Box key={sale.name} sx={{
                            display: 'flex',
                            alignItems: 'center',
                            border: '1px solid',
                            borderColor: 'divider',
                            borderRadius: 1,
                            padding: 1,
                            marginTop: 1,
                            width: 'fit-content',
                            color: 'text.secondary',
                            '& svg': {
                              m: 1,
                            },
                            '& hr': {
                                mx: 0.5,
                                borderColor: 'text.secondary',
                                my: 0,
                              },
                          }} >
                            <Typography variant="body2">{sale.name}</Typography>
                            <Divider orientation="vertical" variant="middle" flexItem />
                            <Typography variant="body2">{sale.start}</Typography>
                            {sale.started ? <Chip className='mx-1' color="primary" label='Started'/> : <Chip className='mx-1' color="secondary" label='Soon'/>}
                        </Box>
                    )}
                </Grid>
            </Grid>
            </CardContent>
        </Card>
        </Container>
        </a>
    );
    };

export default Event;
