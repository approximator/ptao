import React, { Component } from 'react';
import { Button } from 'semantic-ui-react'
import Gallery from 'react-grid-gallery';
import KeyboardEventHandler from 'react-keyboard-event-handler';

class PhotosPage extends Component {

    state = {
        photos: [],
        currentImage: 0,
        lightboxOpened: false,
        totalPhotosCount: undefined,
        shiftPressed: false
    }

    constructor(props) {
        super(props)

        this.onCurrentImageChange = this.onCurrentImageChange.bind(this);
        this.onSelectImage = this.onSelectImage.bind(this);
    }

    componentDidMount() {
        this.fetchPhotos()
    }

    fetchPhotos() {
        const params = new URLSearchParams(this.props.location.search);
        const url = '/api/photos' + this.props.location.search
        console.log('Requesting: ' + url)
        fetch(url)
            .then(res => res.json())
            .then(data => {
                console.log(data);
                this.setState({ photos: data.photos.map(photo => this.createImgObj(params.has("missing"), photo)) });
            })
    }

    onClickSelectAll () {
        let photos = this.state.photos.slice();
        const isAllSelected = photos.filter(photo => photo.isSelected === true).length === photos.length

        photos.forEach(img => { img.isSelected = !isAllSelected; });
        this.setState({
            photos: photos
        });
    }

    onSelectImage(index, image) {
        var photos = this.state.photos.slice();
        var img = photos[index];
        img.isSelected = img.hasOwnProperty("isSelected") ? !img.isSelected : true;

        this.setState({
            photos: photos
        });
    }

    onCurrentImageChange(index) {
        this.setState({ currentImage: index });
    }

    getSelectedImages() {
        return this.state.photos.filter(photo => photo.isSelected === true);
    }

    createImgObj(is_missing, photo) {
        return {
            id: photo.id,
            owner_id: photo.owner_id,
            src: is_missing ? photo.url : photo.local_url,
            thumbnail: is_missing ? photo.url : photo.local_url,
            caption: photo.owner.first_name + ' ' + photo.owner.last_name,
            thumbnailWidth: photo.width,
            thumbnailHeight: photo.height
        }
    }

    removeImages(imgs) {
        console.log(imgs)
        const data = {
            photos: imgs.map(img => img.id)
        }

        const options = {
            method: 'delete',
            headers: {'Content-type': 'application/json; charset=UTF-8'},
            body: JSON.stringify(data)
        }

        fetch('/api/photos', options)
            .then(response => response.json())
            .then(body => {
                console.log(body)
                this.setState({ photos: this.state.photos.filter(photo => !imgs.includes(photo)) });
            })
            .catch(err => console.error(err))
    }

    removeSelectedImages() {
        let selectedImgs = this.getSelectedImages()
        this.removeImages(selectedImgs)
    }

    render() {
        var photos = this.state.photos.map((i) => {
            i.customOverlay = (
                <div style={captionStyle}>
                    <div>{i.caption}</div>
                </div>);
            return i;
        });

        return (
            <div>
                <Button compact toggle active={this.state.selectAllChecked} onClick={() => this.onClickSelectAll()}>
                    Select All
                </Button>

                <Button compact negative onClick={() => this.removeSelectedImages()}>
                    Remove
                </Button>

                <Gallery
                    images={photos}
                    rowHeight={250}
                    onSelectImage={this.onSelectImage}
                    currentImageWillChange={this.onCurrentImageChange}
                    lightboxWillOpen={() => this.setState({lightboxOpened: true})}
                    lightboxWillClose={() => this.setState({lightboxOpened: false})}

                    customControls={[
                        <Button icon='images' onClick={() => {
                            const searchParams = new URLSearchParams();
                            searchParams.set("owner_id", this.state.photos[this.state.currentImage].owner_id);
                            window.location.href = `/photos/?${searchParams.toString()}`;
                        }}/>
                    ]}
                />

                <KeyboardEventHandler
                    handleKeys={['del', 'shift']}
                    onKeyEvent={(key, e) => {
                        if (key === "del") {
                            if (this.state.lightboxOpened) {
                                this.removeImages([this.state.photos[this.state.currentImage].id]);
                            } else {
                                this.removeSelectedImages();
                            }
                        }
                    }}
                >
                </KeyboardEventHandler>
            </div>
        );
    }
}

const captionStyle = {
    backgroundColor: "rgba(0, 0, 0, 0.8)",
    maxHeight: "240px",
    overflow: "hidden",
    position: "absolute",
    bottom: "0",
    width: "100%",
    color: "white",
    padding: "2px",
    fontSize: "90%"
};

export default PhotosPage;
