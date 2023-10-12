from collections import Counter
import streamlit as st
from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo

from .general import country_flags, sector_emojis, sector_colors


class Portfolio:
	def __init__(self):
		self.max_weight = 100.
		self.cards = None
		self.ascending = False
		self.upper_limit = False
		self.sectors = None
		self.countries = None
		self.stats = None

	def populate(self, cards):
		self.max_weight = max(10., min(float(int(420 / len(cards))//10*10), 100.))
		self.delta = self.max_weight / 50
		for c in cards:
			c.weight = 100/len(cards)
			c.max_weight = self.max_weight
			c.set_portfolio(self)
		self.cards = cards
		self.sectors = [k for k, v  in Counter(c.sector for c in cards).most_common()]
		self.countries = [k for k, v  in Counter(c.country for c in cards).most_common()]
		self.stats = list(cards[0].features)

	def update_weights(self, deltas: dict['Card', float]):
		locked = [c for c in deltas if c.locked]
		assert len(locked) == 0, f'Cannot update weight of {len(locked)} locked cards: {locked}'

		other = [c for c in self.cards if c not in deltas and not c.locked]

		if not len(other):
			st.error(f'Cannot update weights, there are no others')
			return

		fixed = {card: max(-card.weight, min(delta, self.max_weight - card.weight))
					for card, delta in deltas.items()}
		total = sum(fixed.values())
		avail = sum(c.weight for c in other)

		if total > 0:
			if total > avail:
				st.error(f'Cannot update weights, {total} > {avail}')
				return
			fixed.update({card: -total * card.weight / avail for card in other})

		elif total < 0:
			cap = sum(self.max_weight - c.weight for c in other)
			if -total > cap:
				st.error(f'Cannot update weights, {-total} > {cap}')
				return
			fixed.update({card: -total * (self.max_weight - card.weight) / cap for card in other})

		assert abs(sum(fixed.values())) < 0.001, f'{fixed}'

		for card, delta in fixed.items():
			card.weight += delta

		assert abs(100 - sum(c.weight for c in self.cards)) < 0.001, f'{sum(c.weight for c in self.cards)}'

	def _select_all(self):
		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				num_sel += 1
				if not c.selected:
					num_new += 1
				c.selected = True
		st.toast(f'Selected {num_sel} stocks ({num_new} new)')

	def _deselect_all(self):
		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				num_sel += 1
				if c.selected:
					num_new += 1
				c.selected = False
		st.toast(f'Deselected {num_sel} stocks ({num_new} new)')

	def _invert_selection(self):
		num_sel = 0
		for c in self.cards:
			if not c.hidden:
				c.selected = not c.selected
				if c.selected:
					num_sel += 1
		st.toast(f'Inverted selection ({num_sel} selected)')

	def _show_all(self):
		num_new = 0
		for c in self.cards:
			if c.hidden:
				num_new += 1
			c.hidden = False
			c.selected = False
		st.toast(f'Showing all ({num_new} were hidden)')

	def _hide_selected(self):
		num_hidden = 0
		for c in self.cards:
			if c.selected:
				num_hidden += 1
				c.hidden = True
				c.selected = False
		st.toast(f'{num_hidden} stocks hidden')

	def _lock_hidden(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if c.hidden:
				num_locked += 1
				if not c.locked:
					num_new += 1
				c.locked = True
		st.toast(f'Locked {num_locked} stocks ({num_new} new)')

	def _lock_selected(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if not c.hidden and c.selected:
				num_locked += 1
				if not c.locked:
					num_new += 1
				c.locked = True
		st.toast(f'Locked {num_locked} stocks ({num_new} new)')

	def _unlock_selected(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if not c.hidden and c.selected:
				num_locked += 1
				if c.locked:
					num_new += 1
				c.locked = False
		st.toast(f'Unlocked {num_locked} stocks ({num_new} new)')

	def _toggle_sort_order(self):
		self.ascending = not self.ascending

	def _toggle_bound(self):
		self.upper_limit = not self.upper_limit

	def _apply_selection(self, select_sectors, select_country, select_stat, side, threshold):

		sectors = [s for s in select_sectors if s in self.sectors]
		countries = [c for c in select_country if c in self.countries]
		stat = select_stat if select_stat in self.stats else None

		# print(f'Selecting by {select_stat!r} {side!r} {threshold!r}')

		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				sector, country = c.sector, c.country
				val = c.weight if stat is None and select_stat == 'Weight' else c.features.get(stat)
				if ((len(sectors) and sector in sectors)
						or (len(countries) and country in countries)
						or (val is not None and threshold is not None
							and ((side == 'Max' and val <= threshold)
								 or (side == 'Min' and val >= threshold)))):
					if not c.selected:
						num_new += 1
					c.selected = True
					num_sel += 1

		st.toast(f'Selected {num_sel} stocks ({num_new} new)')


	def _apply_sort(self, group_sector, group_country, group_stat, ascending):
		# st.write(f'Sorting by {group_sector} and {group_country} and {group_stat}')

		sectors = [s for s in group_sector if s in self.sectors]
		countries = [c for c in group_country if c in self.countries]
		stat = group_stat if group_stat in self.stats else None

		def key(card):
			sector, country = card.sector, card.country
			terms = []
			if stat is not None:
				val = card.features[stat]
				if val is None:
					val = (-1)**(ascending) * float('inf')
				terms.append(val)
			if len(sectors):
				terms.append(tuple(sector == s for s in sectors))
			if len(countries):
				terms.append(tuple(country == c for c in countries))
			return tuple(terms)
		self.cards.sort(key=key, reverse=not ascending)


	# def _change_delta(self):
	# 	self.delta = st.session_state.delta

	def _update_selected(self, delta):
		return self.update_weights({c: delta for c in self.cards if not c.hidden and not c.locked and c.selected})


	def display(self):
		control_col, viz_col = st.columns([1, 2 if st.session_state.sidebar_state == 'expanded' else 5])

		with control_col:

			ctab, ftab = st.tabs(['Controls', 'Checkpointing'])

			with ctab:
				# st.header(f'Controls')
				st.subheader('Change 🔶')
				col1, col2, col3 = st.columns([4, 1, 1])
				with col1:
					delta = st.slider('Weight', 0., self.max_weight / 5, self.max_weight / 40,
									  label_visibility='collapsed')
				with col2:
					inc = st.button('🔼', help='Increase selected')
				with col3:
					dec = st.button('🔽', help='Decrease selected')
				if inc or dec:
					self._update_selected((-1)**dec * delta)

				col1, col2, col3, col4 = st.columns(4)
				with col1:
					if st.button('🔶 all', help='Select all'):
						self._select_all()
				with col2:
					if st.button('⬛ all', help='Deselect all'):
						self._deselect_all()
				with col3:
					st.button('🔄 all', help='Invert selection', on_click=self._invert_selection)
				with col4:
					st.button('Show all', help='Show all hidden', on_click=self._show_all) # 👁

				col1, col2, col3, col4 = st.columns(4)
				with col1:
					st.button('🔒🔶', help='Lock selected', on_click=self._lock_selected)
				with col2:
					st.button('🔓🔶', help='Unlock selected', on_click=self._unlock_selected)
				with col3:
					st.button('💭🔶', help='Hide selected', on_click=self._hide_selected)
				with col4:
					st.button('🔒💭', help='Lock all hidden', on_click=self._lock_hidden)

				hidden = [c for c in self.cards if c.hidden]
				selected = [c for c in self.cards if c.selected]
				st.write(f'Showing {len(self.cards) - len(hidden)} of {len(self.cards)} stocks '
						 f'({len(selected)} selected).')

				col1, col2, col3, col4 = st.columns([2,1,1,1])
				with col1:
					st.subheader(f'Sort')
				with col2:
					st.button('🔼' if self.ascending else '🔽',
							  help='Sort ascending/descending', on_click=self._toggle_sort_order)
				with col3:
					if st.button('💰', help='Sort by weight'):
						self.cards.sort(key=lambda c: c.weight, reverse=not self.ascending)
				with col4:
					if st.button('🔶', help='Sort by selected'):
						self.cards.sort(key=lambda c: c.selected, reverse=not self.ascending)
				with st.form('sort_form', clear_on_submit=True):
					# col1, col2 = st.columns([1,2])
					sort_cards = st.form_submit_button('Apply')

					group_sector = st.multiselect('Group sector', self.sectors, key='group_sector')
					group_country = st.multiselect('Group country', self.countries, key='group_country')
					group_stat = st.selectbox('by Stat', ['', *self.stats], key='group_stat')

					# print(f'{group_sector}, {st.session_state.get("group_sector", None)}')

				if sort_cards:
					self._apply_sort(group_sector, group_country, group_stat, self.ascending)

				st.subheader(f'Selection')
				with st.form('select_form', clear_on_submit=True):
					select_cards = st.form_submit_button('Apply')

					select_sectors = st.multiselect('Select sectors', self.sectors)
					select_country = st.multiselect('Select country', self.countries)

					d_col, q_col = st.columns([2, 1])
					with d_col:
						select_stat = st.selectbox('Feature', ['Weight', *self.stats])
					# st.button('↘️' if self.upper_limit else '↗️', help='Select higher/lower than limit',)
					with q_col:
						side = st.radio('Limit', ['Max', 'Min'], index=0, )#label_visibility='collapsed')
					threshold = st.number_input('Weight', 0., self.max_weight, None, label_visibility='collapsed')


				if select_cards:
					self._apply_selection(select_sectors, select_country, select_stat, side, threshold)

			with ftab:
				st.header('Checkpointing')

				st.write(f'[Coming soon]')

		with st.sidebar:
			st.header('Cards')

			# st.divider()

			for card in self.cards:
				if not card.hidden:
					card.display()


		with viz_col:
			st.write(f'Total weight: {sum(card.weight for card in self.cards):.2f}')




		# layout = [
		#     dashboard.Item("cards", 0, 0, 6, 4),
		# ]
		# with elements("demo"):
		# 	with dashboard.Grid(layout, draggableHandle=".draggable"):
		# 		with mui.Card(key="cards", sx={"display": "flex", "flexDirection": "column"}):
		# 			mui.CardHeader(title="Cards", className="draggable")
		# 			with mui.CardContent(sx={"flex": 1, "minHeight": 4, 'minWidth': 3}):
		#
		# 				mui.Typography("Hello world")
		#
		# 			with mui.CardActions:
		# 				mui.Button("Apply changes")

			# st.title('Stocks')
			# for card in self.cards:
			# 	if not card.hidden:
			# 		card.display()



class Card:
	def __init__(self, info, features, max_weight=100.):
		self.info = info
		self.features = features
		self.p = None
		self.weight = 1.
		self.max_weight = 100.
		self.locked = False
		self.selected = False
		self.hidden = False

	@property
	def name(self):
		return self.info['company_name']
		# return self.info['ticker']

	@property
	def sector(self):
		return str(self.info['sector'])

	@property
	def country(self):
		return str(self.info['country'])

	def set_portfolio(self, portfolio):
		self.p = portfolio

	def toggle_lock(self):
		self.locked = not self.locked

	def toggle_select(self):
		self.selected = not self.selected
		# st.write(f'{self.name} is selected: {self.selected}')

	def update_weight(self):
		self.p.update_weights({self: float(st.session_state[f'weight_{self.name}']) - self.weight})
		# return self.weight

	def display(self):
		with st.container():
			title = self.name
			terms = []
			if self.country in country_flags:
				terms.append(country_flags[self.country])
			if self.sector in sector_emojis:
				terms.append(sector_emojis[self.sector])
			terms.append(self.name)
			title = ' '.join(terms)

			with st.expander(title):
				st.write(f'Details for {self.info["company_name"]}')

			s_col, w_col, l_col = st.columns([1, 3, 1])

			with s_col:
				st.button('🔶' if self.selected else '⬛', key=f'select_{self.name}', on_click=self.toggle_select)
			with w_col:
				st.slider('Weight', 0., self.max_weight,
										self.weight,
										key=f'weight_{self.name}',
										disabled=self.locked, on_change=self.update_weight, label_visibility='collapsed')
				# st.markdown(f'<p style="color:#333;">{self.name}</p>', unsafe_allow_html=True)
			with l_col:
				st.button('🔓' if self.locked else '🔒', key=f'lock_{self.name}', on_click=self.toggle_lock)

			# st.divider()











