import React, { Component } from 'react';
import { Item, Grid, Modal, Dropdown, Button, Icon, Checkbox, Label, Message, Segment } from 'semantic-ui-react';
import { connect } from 'react-redux';
import { fetchUsers, tagPeopleDialogClose, saveUserTags } from '../actions/usersAction';

class TagPeopleDialog extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedPeople: [],
            selectedAuthors: [],
            overwritePeopleTags: false,
            overwriteAuthorsTags: false
        };
    }

    componentWillMount() {
        console.log('componentWillMount. Props', this.props);
        this.props.fetchUsers();
    }

    render() {
        if (!this.props.photos) {
            return null;
        }
        return (
            <Modal
                size="large"
                style={{ minHeight: '80%' }}
                open={this.props.isOpen}
                onClose={this.props.tagPeopleDialogClose}
            >
                <Modal.Header>
                    {this.props.showMessage && (
                        <Message
                            floating
                            success={this.props.result === 'success'}
                            header={this.props.message}
                            style={{ position: 'fixed', left: 1, bottom: 1 }}
                        />
                    )}
                    <Icon name="tag" />
                    Tag People
                </Modal.Header>
                <Modal.Content scrolling>
                    <Grid columns={2} relaxed divided style={{ height: '100vh' }}>
                        <Grid.Column>
                            <Item.Group>
                                {this.props.photos.map(ph => (
                                    <Item key={ph.id}>
                                        <Item.Image
                                            size="small"
                                            label={{
                                                color: 'blue',
                                                content: ph.onwer_name,
                                                icon: 'copyright',
                                                ribbon: true
                                            }}
                                            src={ph.src}
                                        />
                                        <Item.Content verticalAlign="middle">
                                            {ph.people_tags.map(tag => (
                                                <Label
                                                    key={`${ph.id}_${tag.id}_label`}
                                                    icon="user"
                                                    content={`${tag.first_name} ${tag.last_name}`}
                                                />
                                            ))}
                                        </Item.Content>
                                    </Item>
                                ))}
                            </Item.Group>
                        </Grid.Column>
                        <Grid.Column>
                            <Segment padded>
                                <Label attached="top left">
                                    <Icon name="user" />
                                    People on photos
                                </Label>
                                <Checkbox
                                    toggle
                                    label="Overwrite"
                                    onChange={(e, { checked }) => this.setState({ overwritePeopleTags: checked })}
                                />
                                <br />
                                <Dropdown
                                    search
                                    selection
                                    multiple
                                    placeholder="Choose someone"
                                    options={this.props.peopleDropdownList}
                                    onChange={(e, { value }) => {
                                        this.setState({ selectedPeople: value });
                                    }}
                                />
                            </Segment>
                            <Segment padded>
                                <Label attached="top left">
                                    <Icon name="copyright" />
                                    Authors
                                </Label>
                                <Checkbox
                                    toggle
                                    label="Overwrite"
                                    onChange={(e, { checked }) => this.setState({ overwriteAuthorsTags: checked })}
                                />
                                <br />
                                <Dropdown
                                    search
                                    selection
                                    multiple
                                    placeholder="Choose someone"
                                    options={this.props.peopleDropdownList}
                                    onChange={(e, { value }) => {
                                        this.setState({ selectedAuthors: value });
                                    }}
                                />
                            </Segment>
                        </Grid.Column>
                    </Grid>
                </Modal.Content>
                <Modal.Actions>
                    <Button
                        color="green"
                        inverted
                        onClick={() =>
                            this.props.saveUserTags(
                                this.props.photos,
                                this.state.selectedPeople,
                                this.state.selectedAuthors,
                                this.state.overwritePeopleTags,
                                this.state.overwriteAuthorsTags
                            )
                        }
                    >
                        <Icon name="checkmark" /> Save
                    </Button>
                    <Button color="yellow" inverted onClick={this.props.tagPeopleDialogClose}>
                        <Icon name="close" /> Close
                    </Button>
                </Modal.Actions>
            </Modal>
        );
    }
}

function mapStateToProps(state) {
    return {
        ...state.userReducer
    };
}

export default connect(mapStateToProps, { tagPeopleDialogClose, saveUserTags, fetchUsers })(TagPeopleDialog);
