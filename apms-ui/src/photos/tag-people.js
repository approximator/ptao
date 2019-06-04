import React, { Component } from 'react';
import { Item, Grid, Modal, Dropdown, Button, Icon, Checkbox, Label, Message } from 'semantic-ui-react';
import { connect } from 'react-redux';
import { fetchUsers, tagPeopleDialogClose, saveUserTags } from '../actions/usersAction';

class TagPeopleDialog extends Component {
    componentWillMount() {
        console.log('componentWillMount. Props', this.props);
        this.props.fetchUsers();
    }

    render() {
        if (!this.props.photos) {
            return null;
        }
        return (
            <Modal size="large" open={this.props.isOpen} onClose={this.props.tagPeopleDialogClose}>
                <Modal.Header>
                    {this.props.success !== 'unknown' && (
                        <Message floating success={this.state.success === 'success'} header={this.state.success} />
                    )}
                    Tag People
                </Modal.Header>
                <Modal.Content scrolling>
                    <Grid columns={2} relaxed divided>
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
                                                    key={`${ph.id}_label`}
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
                            <Checkbox
                                toggle
                                label="Overwrite"
                                onChange={(e, { checked }) => this.setState({ overwriteTags: checked })}
                            />
                            <br />
                            <Dropdown
                                search
                                selection
                                multiple
                                placeholder="Choose someone"
                                options={this.props.peopleDropdownList}
                                onChange={(e, { value }) => {
                                    this.setState({ selectedUsers: value });
                                }}
                            />
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
                                this.state.selectedUsers,
                                this.state.overwriteTags
                            )
                        }
                    >
                        <Icon name="checkmark" /> Save
                    </Button>
                    <Button color="yellow" inverted onClick={this.onClose}>
                        <Icon name="close" /> Close
                    </Button>
                </Modal.Actions>
            </Modal>
        );
    }
}

function mapStateToProps(state) {
    return {
        photos: state.userReducer.photos,
        isOpen: state.userReducer.tagUsersDialogOpen,
        peopleDropdownList: state.userReducer.peopleDropdownList,
        success: state.userReducer.success
    };
}

export default connect(
    mapStateToProps,
    { tagPeopleDialogClose, saveUserTags, fetchUsers }
)(TagPeopleDialog);
