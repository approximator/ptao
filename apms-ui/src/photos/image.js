import React from 'react';
import { Icon } from 'semantic-ui-react';
import { NavLink } from 'react-router-dom';
import { makeSearchParams } from '../utils/urlParams';

const Checkmark = ({ selected }) => (
    <div style={selected ? { left: '4px', top: '4px', position: 'absolute', zIndex: '1' } : { display: 'none' }}>
        <svg style={{ fill: 'white', position: 'absolute' }} width="24px" height="24px">
            <circle cx="12.5" cy="12.2" r="8.292" />
        </svg>
        <svg style={{ fill: '#06befa', position: 'absolute' }} width="24px" height="24px">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
        </svg>
    </div>
);

const imgStyle = {
    transition: 'transform .135s cubic-bezier(0.0,0.0,0.2,1),opacity linear .15s'
};
const selectedImgStyle = {
    transform: 'translateZ(0px) scale3d(0.9, 0.9, 1)',
    transition: 'transform .135s cubic-bezier(0.0,0.0,0.2,1),opacity linear .15s'
};
const cont = {
    backgroundColor: '#eee',
    cursor: 'pointer',
    overflow: 'hidden',
    position: 'relative'
};

const Image = ({ index, onClick, photo, margin, direction, top, left }) => {
    //calculate x,y scale
    const sx = (100 - (30 / photo.width) * 100) / 100;
    const sy = (100 - (30 / photo.height) * 100) / 100;
    selectedImgStyle.transform = `translateZ(0px) scale3d(${sx}, ${sy}, 1)`;

    if (direction === 'column') {
        cont.position = 'absolute';
        cont.left = left;
        cont.top = top;
    }
    return (
        <div
            style={{ margin, height: photo.height, width: photo.width, ...cont }}
            className={!photo.selected ? 'not-selected' : ''}
        >
            <Checkmark selected={photo.selected ? true : false} />
            <img
                onClick={e => onClick(e, { index, photo })}
                alt=""
                style={photo.selected ? { ...imgStyle, ...selectedImgStyle } : { ...imgStyle }}
                src={photo.src}
                width={photo.width}
                height={photo.height}
            />
            <style>{`.not-selected:hover{outline:2px solid #06befa}`}</style>

            <div style={captionStyle}>
                <NavLink
                    key={photo.owner_id}
                    style={peopleTagsStyle}
                    to={{
                        pathname: '/photos',
                        search: makeSearchParams({ page: 1, owner_id: photo.owner_id }, window.location.search)
                    }}
                >
                    <Icon name="rss" />
                    {photo.onwer_name}
                </NavLink>

                {photo.authors.map(author => (
                    <NavLink
                        key={author.id}
                        style={peopleTagsStyle}
                        to={{
                            pathname: '/photos',
                            search: makeSearchParams({ page: 1, photos_by: author.id }, window.location.search)
                        }}
                    >
                        <Icon name="copyright" />
                        {`${author.first_name} ${author.last_name}`}
                    </NavLink>
                ))}

                {photo.people_tags.map(tag => (
                    <NavLink
                        key={tag.id}
                        style={peopleTagsStyle}
                        to={{
                            pathname: '/photos',
                            search: makeSearchParams({ page: 1, photos_of: tag.id }, window.location.search)
                        }}
                    >
                        <Icon name="user" />
                        {`${tag.first_name} ${tag.last_name}`}
                    </NavLink>
                ))}
            </div>
        </div>
    );
};

// const hostLinkStyle = {
//     pointerEvents: 'auto'
// };

const peopleTagsStyle = {
    pointerEvents: 'auto',
    wordWrap: 'break-word',
    display: 'inline-block',
    backgroundColor: 'rgba(.5, .5, 0, 0.2)',
    height: 'auto',
    fontSize: '75%',
    fontWeight: '600',
    lineHeight: '1',
    padding: '.2em .6em .3em',
    borderRadius: '.25em',
    color: 'white',
    verticalAlign: 'baseline',
    margin: '2px'
};

const captionStyle = {
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    overflow: 'hidden',
    position: 'absolute',
    bottom: '0',
    width: '100%',
    color: 'white',
    padding: '2px'
};

export default Image;
