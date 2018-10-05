import React, { Component } from 'react';
import { List, Grid, Image, Modal, Dropdown, Button, Icon, Checkbox } from 'semantic-ui-react'

class TagPeopleDialog extends Component {

    state = {
        modalOpen: false,
        overwriteTags: false,
        photos: [],
        allPeople: [],
        selectedUsers: []
    }

    constructor(props) {
        super(props);
        this.saveUserTags = this.saveUserTags.bind(this);
    }

    componentDidMount() {
        fetch('/api/users')
            .then(res => res.json())
            .then(data => this.setState({ allPeople: data.users }));
    }

    componentWillReceiveProps(newProps) {
        this.setState({
            modalOpen: newProps.modalOpen,
            photos: newProps.photos
        })
    }

    saveUserTags() {
        const data = {
            photos: this.state.photos.map(ph => ph.id),
            people: this.state.selectedUsers.map(user => user.id),
            overwriteTags: this.state.overwriteTags
        }

        const options = {
            method: 'put',
            headers: { 'Content-type': 'application/json; charset=UTF-8' },
            body: JSON.stringify(data)
        }

        fetch('/api/photos/tagPeople', options)
            .then(response => response.json())
            .then(body => {
                console.log(body)
            })
            .catch(err => console.error(err))
    }

    render() {
        const allPeopleOptions =
            <Dropdown search selection multiple
                placeholder='Choose someone'
                options={this.state.allPeople.map((user) => {
                    return { key: user.id, value: user, text: `${user.first_name} ${user.last_name}` };
                })}
                onChange={(e, { value }) => {
                    this.setState({ selectedUsers: value });
                }}
            />

        const photosList = this.state.photos.map((ph) =>
            <List.Item>
                <Image avatar src={ph.src} />
                <List.Content>
                    <List.Header as='a'>{ph.onwer_name}</List.Header>
                </List.Content>
            </List.Item>
        )

        return (
            <Modal open={this.state.modalOpen}>
                <Modal.Header>Tag People</Modal.Header>
                <Modal.Content>
                    <Grid columns={2} relaxed divided>
                        <Grid.Column>
                            <List>
                                <List.Item>
                                    <List.Header>Photos to tag</List.Header>
                                </List.Item>
                                {photosList}
                            </List>
                        </Grid.Column>
                        <Grid.Column>
                            <Checkbox toggle label='Overwrite' onChange={(e, { checked }) => this.setState({ overwriteTags: checked })} /><br />
                            {allPeopleOptions}
                        </Grid.Column>
                    </Grid>
                </Modal.Content>
                <Modal.Actions>
                    <Button color='green' inverted onClick={this.saveUserTags}>
                        <Icon name='checkmark' /> Save
                    </Button>
                </Modal.Actions>
            </Modal>
        );
    }
}

export default TagPeopleDialog;
